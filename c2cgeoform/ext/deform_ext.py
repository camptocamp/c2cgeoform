import json
import logging
import os
from io import BufferedRandom, BytesIO
from typing import Any, Callable, Optional, Union

import colander
import deform.field
import pyramid.interfaces
import pyramid.request
import requests
import sqlalchemy.orm
from colander import Invalid
from deform.compat import string_types
from deform.widget import CheckboxChoiceWidget
from deform.widget import FileUploadWidget as DeformFileUploadWidget
from deform.widget import MappingWidget, RadioChoiceWidget, Select2Widget, SelectWidget, Widget
from sqlalchemy import inspect
from translationstring import TranslationString, TranslationStringFactory

from c2cgeoform import JSON, JSONDict, default_map_settings

_ = TranslationStringFactory("c2cgeoform")
log = logging.getLogger(__name__)


class MapWidget(Widget):  # type: ignore[misc]
    """
    A Deform widget that fits with GeoAlchemy 2 geometry columns and shows
    an OpenLayers map which allows to draw and modify geometries.

    Example usage

    .. code-block:: python

        geom = Column(
            geoalchemy2.Geometry('POLYGON', 4326), info={
                'colanderalchemy': {
                    'typ': colander_ext.Geometry(
                        'POLYGON', srid=4326, map_srid=3857),
                    'widget': deform_ext.MapWidget(
                        map_options={
                            'baseLayers': [{'type_': 'OSM'}],
                            'view':
                                'projection': 'EPSG:3857',
                                'center': [829170, 5933942],
                                'zoom': 7,
                            'fitMaxZoom': 14,
                            'focusOnly': False
                        }
                    )
                }})

    **Attributes/Arguments**

    map_options (dict, optional):
        Options for the map with:

        - baseLayers (list, optional): List of layer definitions.

        - view (dict, optional): View parameters (projection, center, zoom)

        - fitMaxZoom (int, optional): Maximum zoom when fitting to given geometry.

        - focusOnly (boolean, optional): If map has to be focused for interactions to work.

    If those parameters are not sufficient to customize the map,
    the template file `map.pt` can to be overwritten in application project.
    """

    requirements: tuple[tuple[str, Optional[str]], ...] = tuple()

    map_options = default_map_settings

    def serialize(
        self,
        field: deform.field.Field,
        cstruct: Union[str, colander._null],
        readonly: bool = False,
        **kw: Any,
    ) -> str:
        if cstruct is colander.null:
            cstruct = ""
        values = self.get_template_values(field, cstruct, kw)
        map_options = {
            key: (
                field.parent.schema.request.translate(value)
                if isinstance(value, TranslationString)
                else value
            )
            for key, value in self.map_options.items()
        }
        values["map_options"] = {**self._get_controls_definition(field, readonly), **map_options}
        # make `_` available in template for i18n messages
        values["_"] = _
        return field.renderer("map", **values)  # type: ignore[no-any-return]

    def deserialize(self, field: deform.field.Field, pstruct: str) -> str:
        return pstruct

    def _get_controls_definition(self, field: deform.field.Field, readonly: bool) -> JSONDict:
        geometry_type = field.typ.geometry_type

        point = True
        line = True
        polygon = True
        is_multi_geometry = False

        if "POINT" in geometry_type:
            line = False
            polygon = False
        elif "LINESTRING" in geometry_type:
            point = False
            polygon = False
        elif "POLYGON" in geometry_type:
            point = False
            line = False

        if "MULTI" in geometry_type or geometry_type == "GEOMETRY" or geometry_type == "GEOMETRYCOLLECTION":
            is_multi_geometry = True

        return {
            "point": point,
            "line": line,
            "polygon": polygon,
            "isMultiGeometry": is_multi_geometry,
            "readonly": readonly,
        }


class RelationSelectMixin:
    """
    Mixin class to support relations for select fields.
    """

    def __init__(
        self,
        model: type[Any],
        id_field: str,
        label_field: str,
        default_value: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> None:
        self.model = model
        self.id_field = id_field
        self.label_field = label_field
        self.default_value = default_value
        self.order_by = order_by

    def populate(self, session: sqlalchemy.orm.Session, request: pyramid.request.Request) -> None:
        del request  # unused
        self.values = self._get_select_values(session)

    def _get_select_values(self, session: sqlalchemy.orm.Session) -> tuple[Union[str, tuple[str, str]], ...]:
        model = inspect(self.model)
        if self.order_by is not None:
            order_by = getattr(model.columns, self.order_by)
        else:
            order_by = None

        entities = session.query(model).order_by(order_by)

        values: tuple[tuple[str, str], ...] = tuple(
            (getattr(entity, self.id_field), getattr(entity, self.label_field)) for entity in entities
        )

        if self.default_value is None:
            return values
        else:
            return (self.default_value,) + values


class RelationMultiSelectMixin(RelationSelectMixin):
    """
    Mixin class to support n:m relations for multi select fields.
    """

    def deserialize(self, field: deform.field.Field, pstruct: str) -> list[JSONDict]:
        """
        Deserialize the field input for a n:m relation.

        For example for a n:m relation between mapper A and mapper B and a
        relation table A_B: Let's assume this widget is used in model A, so
        that you can select entries of B. Then this method will receive a list
        of ids of table B. For each id it will create an object containing the
        id. These objects will be inserted in the relation table A_B.
        """
        if pstruct in (colander.null, None):
            return []
        ids = pstruct

        # get the id field of the mapped table B in the relation table A_B
        mapped_id_field = self._get_mapped_id_field(field)

        result = []
        if ids:
            assert mapped_id_field is not None
            for id_ in ids:
                # create an entry for the relation table A_B
                obj = {}
                # set the id for an entity of the mapped table B,
                # the id for an entity of table A will be filled in automatically
                obj[mapped_id_field.name] = mapped_id_field.deserialize(id_)
                result.append(obj)

        return result

    def serialize(
        self, field: deform.field.Field, cstruct: Optional[Union[colander._null, str]], **kw: Any
    ) -> list[str]:
        """
        Flatten a list of objects into a list of ids.
        """
        del kw  # unused

        mapped_id_field = self._get_mapped_id_field(field)
        # create a list with only the ids of entities of table B
        if cstruct in (colander.null, None):
            cstruct = []
        assert cstruct is not None
        assert mapped_id_field is not None
        return [obj[mapped_id_field.name] for obj in cstruct]

    def _get_mapped_id_field(self, field: deform.field.Field) -> Optional[deform.field.Field]:
        """
        For the given relation field in table A, find the foreign key field
        for table B in the relation table A_B.
        """
        relation_field = field.children[0]

        for subfield in relation_field.children:
            if subfield.name == self.id_field:
                return subfield
        return None


class RelationSelectWidget(SelectWidget, RelationMultiSelectMixin):  # type: ignore[misc]
    """
    Extension of the widget ````deform.widget.SelectWidget`` which loads the
    values from the database using a SQLAlchemy model.

    Example usage

    .. code-block:: python

        districtId = Column(Integer, ForeignKey('district.id'), info={
            'colanderalchemy': {
                'title': 'District',
                'widget': deform_ext.RelationSelectWidget(
                    District,
                    'id',
                    'name',
                    order_by='name',
                    default_value=('', _('- Select -'))
                )
            }})

    The values of this ``<select>`` field are filled with entries of model
    ``District``, whereas property ``id`` is used as value and ``name`` as
    label.

    For n:m relations the widget can be used like so:

    .. code-block:: python

        situations = relationship(
            "Situation",
            secondary=situation_for_permission,
            cascade="save-update,merge,refresh-expire",
            info={
                'colanderalchemy': {
                    'title': _('Situations'),
                    'widget': RelationSelectWidget(
                        Situation,
                        'id',
                        'name',
                        order_by='name',
                        multiple=True
                    ),
                    'includes': ['id'],
                    'validator': manytomany_validator
                }
            })

    **Attributes/Arguments**

    model (required)
        The SQLAlchemy model that is used to generate the list of values.

    id_field
        The property of the model that is used as value.
        Default: ``id``.

    label_field
        The property of the model that is used as label.
        Default: ``label``.

    order_by
        The property of the model that is used for the ``order_by`` clause of
        the SQL query.
        Default: ``None``.

    default_value
        A default value that is added add the beginning of the list of values
        that were loaded from the database.
        For example: ``default_value=('', _('- Select -'))``
        Default: ``None``.

    multiple
        Allow to select multiple values. Requires a n:m relationship.
        Default: ``False``.

    For further attributes, please refer to the documentation of
    ``deform.widget.SelectWidget`` in the deform documentation:
    <http://deform.readthedocs.org/en/latest/api.html>

    """

    def __init__(
        self,
        model: type[Any],
        id_field: str = "id",
        label_field: str = "label",
        default_value: Any = None,
        order_by: Optional[str] = None,
        **kw: Any,
    ) -> None:
        RelationMultiSelectMixin.__init__(self, model, id_field, label_field, default_value, order_by)
        SelectWidget.__init__(self, **kw)

    def deserialize(self, field: deform.field.Field, pstruct: str) -> list[JSONDict]:
        if self.multiple:
            return RelationMultiSelectMixin.deserialize(self, field, pstruct)
        else:
            return SelectWidget.deserialize(self, field, pstruct)  # type: ignore[no-any-return]

    def serialize(self, field: deform.field.Field, cstruct: Any, **kw: Any) -> list[str]:
        cstruct_internal = (
            RelationMultiSelectMixin.serialize(self, field, cstruct, **kw) if self.multiple else cstruct
        )
        return SelectWidget.serialize(self, field, cstruct_internal, **kw)  # type: ignore[no-any-return]


class RelationSelect2Widget(Select2Widget, RelationMultiSelectMixin):  # type: ignore[misc]
    """
    Extension of the widget ````deform.widget.Select2Widget`` which loads the
    values from the database using a SQLAlchemy model.

    Example usage

    .. code-block:: python

        districtId = Column(Integer, ForeignKey('district.id'), info={
            'colanderalchemy': {
                'title': 'District',
                'widget': deform_ext.RelationSelect2Widget(
                    District,
                    'id',
                    'name',
                    order_by='name',
                    default_value=('', _('- Select -'))
                )
            }})

    The values of this ``<select>`` field are filled with entries of model
    ``District``, whereas property ``id`` is used as value and ``name`` as
    label.

    For n:m relations the widget can be used like so:

    .. code-block:: python

        situations = relationship(
            "Situation",
            secondary=situation_for_permission,
            cascade="save-update,merge,refresh-expire",
            info={
                'colanderalchemy': {
                    'title': _('Situations'),
                    'widget': RelationSelect2Widget(
                        Situation,
                        'id',
                        'name',
                        order_by='name',
                        multiple=True
                    ),
                    'includes': ['id'],
                    'validator': manytomany_validator
                }
            })

    **Attributes/Arguments**

    model (required)
        The SQLAlchemy model that is used to generate the list of values.

    id_field
        The property of the model that is used as value.
        Default: ``id``.

    label_field
        The property of the model that is used as label.
        Default: ``label``.

    order_by
        The property of the model that is used for the ``order_by`` clause of
        the SQL query.
        Default: ``None``.

    default_value
        A default value that is added add the beginning of the list of values
        that were loaded from the database.
        For example: ``default_value=('', _('- Select -'))``
        Default: ``None``.

    multiple
        Allow to select multiple values. Requires a n:m relationship.
        Default: ``False``.

    For further attributes, please refer to the documentation of
    ``deform.widget.Select2Widget`` in the deform documentation:
    <http://deform.readthedocs.org/en/latest/api.html>

    """

    def __init__(
        self,
        model: type[Any],
        id_field: str = "id",
        label_field: str = "label",
        default_value: Any = None,
        order_by: Optional[str] = None,
        **kw: Any,
    ) -> None:
        RelationMultiSelectMixin.__init__(self, model, id_field, label_field, default_value, order_by)
        Select2Widget.__init__(self, **kw)

    def deserialize(self, field: deform.field.Field, pstruct: str) -> list[JSONDict]:
        if self.multiple:
            return RelationMultiSelectMixin.deserialize(self, field, pstruct)
        else:
            return Select2Widget.deserialize(self, field, pstruct)  # type: ignore[no-any-return]

    def serialize(self, field: deform.field.Field, cstruct: Any, **kw: Any) -> list[str]:
        cstruct_internal = (
            RelationMultiSelectMixin.serialize(self, field, cstruct, **kw) if self.multiple else cstruct
        )
        return Select2Widget.serialize(self, field, cstruct_internal, **kw)  # type: ignore[no-any-return]


class RelationCheckBoxListWidget(CheckboxChoiceWidget, RelationMultiSelectMixin):  # type: ignore[misc]
    """
    Extension of the widget ````deform.widget.CheckboxChoiceWidget`` which
    loads the values from the database using a SQLAlchemy model.

    For n:m relations the widget can be used like so:

    .. code-block:: python

        situations = relationship(
            "Situation",
            secondary=situation_for_permission,
            cascade="save-update,merge,refresh-expire",
            info={
                'colanderalchemy': {
                    'title': _('Situations'),
                    'widget': RelationCheckBoxListWidget(
                        Situation,
                        'id',
                        'name',
                        order_by='name',
                        edit_url=lambda request, value: request.route_url(
                                'c2cgeoform_item',
                                table='situations',
                                id=value
                                )
                    ),
                    'includes': ['id'],
                    'validator': manytomany_validator
                }
            })

    **Attributes/Arguments**

    model (required)
        The SQLAlchemy model that is used to generate the list of values.

    id_field
        The property of the model that is used as value.
        Default: ``id``.

    label_field
        The property of the model that is used as label.
        Default: ``label``.

    order_by
        The property of the model that is used for the ``order_by`` clause of
        the SQL query.
        Default: ``None``.
    edit_url (optional)
        a function taking request and value as parameter and returning
        an url to the corresponding resource.

    For further attributes, please refer to the documentation of
    ``deform.widget.Select2Widget`` in the deform documentation:
    <http://deform.readthedocs.org/en/latest/api.html>
    """

    def __init__(
        self,
        model: type[Any],
        id_field: str = "id",
        label_field: str = "label",
        order_by: Optional[str] = None,
        **kw: Any,
    ) -> None:
        RelationMultiSelectMixin.__init__(self, model, id_field, label_field, None, order_by)
        CheckboxChoiceWidget.__init__(self, multiple=True, **kw)

    def deserialize(self, field: deform.field.Field, pstruct: str) -> list[JSONDict]:
        return RelationMultiSelectMixin.deserialize(self, field, pstruct)

    def serialize(self, field: deform.field.Field, cstruct: Any, **kw: Any) -> list[str]:
        cstruct_internal = RelationMultiSelectMixin.serialize(self, field, cstruct, **kw)
        return CheckboxChoiceWidget.serialize(self, field, cstruct_internal, **kw)  # type: ignore[no-any-return]


class RelationRadioChoiceWidget(RadioChoiceWidget, RelationSelectMixin):  # type: ignore[misc]
    """
    Extension of the widget ````deform.widget.RadioChoiceWidget`` which loads
    the values from the database using a SQLAlchemy model.

    Example usage

    .. code-block:: python

        districtId = Column(Integer, ForeignKey('district.id'), info={
            'colanderalchemy': {
                'title': 'District',
                'widget': deform_ext.RelationRadioChoiceWidget(
                    District,
                    'id',
                    'name',
                    order_by='name'
                )
            }})

    The values of this field are filled with entries of model ``District``,
    whereas property ``id`` is used as value and ``name`` as label.

    **Attributes/Arguments**

    model (required)
        The SQLAlchemy model that is used to generate the list of values.

    id_field
        The property of the model that is used as value.
        Default: ``id``.

    label_field
        The property of the model that is used as label.
        Default: ``label``.

    order_by
        The property of the model that is used for the ``order_by`` clause of
        the SQL query.
        Default: ``None``.

    For further attributes, please refer to the documentation of
    ``deform.widget.RadioChoiceWidget`` in the deform documentation:
    <http://deform.readthedocs.org/en/latest/api.html>

    """

    def __init__(
        self,
        model: type[Any],
        id_field: str = "id",
        label_field: str = "label",
        order_by: Optional[str] = None,
        **kw: Any,
    ) -> None:
        RelationSelectMixin.__init__(self, model, id_field, label_field, None, order_by)
        RadioChoiceWidget.__init__(self, **kw)


class FileUploadTempStore:
    def __init__(self, session: pyramid.interfaces.ISession) -> None:
        super().__init__()
        self.session = session

    def get(self, name: str, default: Any = None) -> Any:
        return self.deserialize(self.session.get(name, default))

    def __getitem__(self, name: str) -> Any:
        return self.deserialize(self.session[name])

    def __setitem__(self, name: str, value: Any) -> None:
        self.session[name] = self.serialize(value)
        self.session.save()

    def __contains__(self, name: str) -> bool:
        return name in self.session

    def serialize(self, data: str) -> str:
        if isinstance(data, dict):
            return {k: self.serialize(v) for k, v in data.items()}
        if isinstance(data, (BufferedRandom, BytesIO)):
            value = data.read()
            # set the file position back to 0, so that the file can be read again
            data.seek(0, os.SEEK_SET)
            return value
        return data

    def deserialize(self, data: str) -> str:
        if isinstance(data, dict):
            return {k: self.deserialize(v) for k, v in data.items()}
        if isinstance(data, bytes):
            return BytesIO(data)
        return data

    def preview_url(self, name: str) -> None:
        pass


class FileUploadWidget(DeformFileUploadWidget):  # type: ignore[misc]
    """Extension of ``deform.widget.FileUploadWidget`` to be used in a model
    class that extends the ``models.FileData`` mixin class.

    Note that, contrary to ``deform.widget.FileUploadWidget``, this extension
    is not meant to be used with the ``deform.FileData`` Colander type. Instead
    it works with the ``colander.Mapping`` type, which is what
    ``colanderalchemy`` uses for an SQLAlchemy model class.

    Note also that it is required to set ``unknown`` to ``'preserve'`` in the
    ``__colanderalchemy_config__`` dictionary.

    Example usage

    .. code-block:: python

        from c2cgeoform import models
        from c2cgeoform.ext import deform_ext

        class Photo(models.FileData, Base):
            __tablename__ = 'photo'
            __colanderalchemy_config__ = {
                'title': _('Photo'),
                'unknown': 'preserve',
                'widget': deform_ext.FileUploadWidget(file_upload_temp_store)
            }
            permission_id = Column(Integer, ForeignKey('excavations.id'))

    **Attributes/Arguments**

    id_field (default to "id")
        Name of field to pass to get_url.

    get_url (optional)
        A callback function `function(request, id) -> string` which returns
        the URL to get the file. Example usage:

        .. code-block:: python

            'widget': deform_ext.FileUploadWidget(
                _file_upload_temp_store,
                id_field="id",
                get_url=lambda request, id: request.route_url('file', id=id)
            )
    """

    id_field = "id"
    request: Optional[pyramid.request.Request] = None

    def __init__(
        self, get_url: Optional[Callable[[pyramid.request.Request, JSON], str]] = None, **kw: Any
    ) -> None:
        DeformFileUploadWidget.__init__(self, None, **kw)
        self.get_url = get_url

    def populate(self, session: sqlalchemy.orm.Session, request: pyramid.request.Request) -> None:
        del session  # unused
        self.request = request
        self.tmpstore = FileUploadTempStore(request.session)

    def serialize(self, field: deform.field.Field, cstruct: JSONDict, **kw: Any) -> str:
        if cstruct in (colander.null, None):
            cstruct = {}
        kw["url"] = None
        if "uid" not in cstruct and self.id_field in cstruct:
            cstruct["uid"] = cstruct[self.id_field]
            if cstruct[self.id_field] != colander.null and self.get_url:
                kw["url"] = self.get_url(self.request, cstruct[self.id_field])
        if cstruct.get("filename", None) == colander.null:
            cstruct["filename"] = ""
        return DeformFileUploadWidget.serialize(self, field, cstruct, **kw)  # type: ignore[no-any-return]

    def deserialize(self, field: deform.field.Field, pstruct: str) -> Any:
        value = DeformFileUploadWidget.deserialize(self, field, pstruct)
        if value != colander.null and "fp" in value:
            value["data"] = value.pop("fp")
        return value


class RelationSelectMapWidget(Widget):  # type: ignore[misc]
    """
    A Deform widget to select an item on a map. From the idea, this widget
    is similar to the ``RelationSelectWidget``, but instead of a select-box
    a map is shown.

    Example usage

    .. code-block:: python

        bus_stop = Column(Integer, ForeignKey('bus_stops.id'), info={
            'colanderalchemy': {
                'title': 'Bus stop',
                'widget': deform_ext.RelationSelectMapWidget(
                    label_field='name', url='/bus_stops'
                )
            }})

    The user is responsible for providing a web-service under the given URL,
    which returns a list of features as GeoJSON. The features must contain the
    two properties specified with `id_field` and `label_field`. The geometries
    are expected to use the CRS `EPSG:4326`.

    To customize the map, the template file `map_select.pt` has to be
    overwritten.

    **Attributes/Arguments**

    url (required)
        The URL to the web-service which returns the GeoJSON features or a
        callback function `function(request: pyramid.request.Request) -> string` which returns the URL
        to the web-service. Example usage:

        .. code-block:: python

            'widget': deform_ext.RelationSelectMapWidget(
                label_field='name',
                url=lambda request: request.route_url('bus_stops')
            )

    label_field
        The property of the GeoJSON features that is used as label.
        Default: ``label``.

    """

    requirements = (
        ("openlayers", "3.0.0"),
        ("c2cgeoform.deform_map", None),
    )

    def __init__(
        self,
        url: Union[str, Callable[[pyramid.request.Request], str]],
        label_field: str = "label",
        **kw: Any,
    ) -> None:
        Widget.__init__(self, **kw)
        self.label_field = label_field
        self.get_url: Callable[[pyramid.request.Request], str] = url if callable(url) else lambda request: url
        self.url = None

    def populate(self, session: sqlalchemy.orm.Session, request: pyramid.request.Request) -> None:
        del session  # unused

        if self.url is None:
            self.url = self.get_url(request)  # type: ignore[assignment]

    def serialize(self, field: deform.field.Field, cstruct: str, readonly: bool = False, **kw: Any) -> str:
        if cstruct is colander.null:
            cstruct = ""
        values = self.get_template_values(field, cstruct, kw)
        # make `_` available in template for i18n messages
        values["_"] = TranslationStringFactory("c2cgeoform")
        values["widget_config"] = json.dumps(
            {"labelField": self.label_field, "url": self.url, "readonly": readonly}
        )
        return field.renderer("map_select", **values)  # type: ignore[no-any-return]

    def deserialize(self, field: deform.field.Field, pstruct: str) -> str:
        return pstruct


class RelationSearchWidget(Widget):  # type: ignore[misc]
    """
    A Deform widget to select an item via a search field. This widget is
    similar to the ``RelationSelectWidget``, but instead of a select-box
    a Twitter Typeahead search field is shown.

    Example usage:

    .. code-block:: python

        address_id = Column(Integer, ForeignKey('address.id'), info={
            'colanderalchemy': {
                'title': _('Address'),
                'widget': deform_ext.RelationSearchWidget(
                    url=lambda request: request.route_url('addresses'),
                    model=Address,
                    min_length=1,
                    id_field='id',
                    label_field='label'
                )
            }})

    The user is responsible for providing a web-service at the given URL.  The
    web service should expect requests of the form ``?term=<search_terms>``.
    And it should return responses of this form:

    .. code-block:: json

        [{"id": 0, "label": "foo"}, {"id": 1, "label": "bar"}]

    The name of the id and label keys are configurable. See below.

    **Attributes/arguments**

    url (required)
        The search service URL, or a function that takes a request a return the
        search service URL.

    model (required)
        The SQLAlchemy model class associated to the linked table.

    min_length
        The minimum character length needed before suggestions start getting
        rendered. Default: ``1``.

    id_field
        The name of the "id" property in JSON responses. Default: ``"id"``.

    label_field
        The name of the "label" property in JSON responses.
        Default: ``"label"``.

    limit
        The maximum number of suggestions. Default: 8.

    """

    id_field = "id"
    label_field = "label"
    limit = 8
    min_length = 1
    readonly_template = "readonly/textinput"
    strip = True
    template = "search"
    requirements = (("typeahead", "0.10.5"),)

    def __init__(self, url: Union[str, Callable[[pyramid.request.Request], str]], **kw: Any) -> None:
        Widget.__init__(self, **kw)
        self.get_url: Callable[[pyramid.request.Request], str] = url if callable(url) else lambda request: url
        self.url = None
        self.session: Optional[sqlalchemy.orm.Session] = None

    def populate(self, session: sqlalchemy.orm.Session, request: pyramid.request.Request) -> None:
        if self.url is None:
            self.url = self.get_url(request)  # type: ignore[assignment]
        self.session = session

    def serialize(self, field: deform.field.Field, cstruct: str, **kw: Any) -> str:
        if cstruct in (colander.null, None):
            cstruct = ""
            label = ""
        else:
            assert self.session is not None
            obj = self.session.query(self.model).get(cstruct)
            label = getattr(obj, kw.get("label_field", self.label_field))

        kw["label"] = label

        options = {
            "idField": kw.pop("id_field", self.id_field),
            "labelField": kw.pop("label_field", self.label_field),
        }
        kw["options"] = json.dumps(options)

        bloodhound_options = {"limit": kw.pop("limit", self.limit), "remote": "%s?term=%%QUERY" % self.url}
        kw["bloodhound_options"] = json.dumps(bloodhound_options)

        typeahead_options = {"minLength": kw.pop("min_length", self.min_length)}
        kw["typeahead_options"] = json.dumps(typeahead_options)

        readonly = kw.get("readonly", self.readonly)

        # If "readonly" is set then deform's readonly "textinput" template will
        # be used. That template will display the value set in "cstruct" so we
        # just set cstruct to label here.
        cstruct = label if readonly else cstruct

        tmpl_values = self.get_template_values(field, cstruct, kw)
        template = self.readonly_template if readonly else self.template

        return field.renderer(template, **tmpl_values)  # type: ignore[no-any-return]

    def deserialize(self, field: deform.field.Field, pstruct: str) -> Optional[Union[colander._null, str]]:
        if pstruct is colander.null:
            return colander.null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if self.strip:
            pstruct = pstruct.strip()
            if not pstruct:
                return colander.null
            return pstruct
        return None


class RecaptchaWidget(MappingWidget):  # type: ignore[misc]
    """
    A Deform widget for Google reCaptcha.

    In `c2cgeoform` this widget can be used by setting the `show_captcha`
    flag when calling `register_schema()`.

    Example usage:

    .. code-block:: python

        register_schema(
            'comment', model.Comment, show_confirmation=False,
            show_captcha=True,
            recaptcha_public_key=settings.get('recaptcha_public_key'),
            recaptcha_private_key=settings.get('recaptcha_private_key'))

    **Attributes/arguments**

    public_key (required)
        The Google reCaptcha site key.

    private_key (required)
        The Google reCaptcha secret key.

    """

    template = "recaptcha"
    readonly_template = "recaptcha"
    url = "https://www.google.com/recaptcha/api/siteverify"
    request: Optional[pyramid.request.Request] = None

    def populate(self, session: sqlalchemy.orm.Session, request: pyramid.request.Request) -> None:
        del session  # unused
        self.request = request

    def serialize(self, field: deform.field.Field, cstruct: JSONDict, **kw: Any) -> MappingWidget:
        assert self.request is not None
        kw.update(
            {
                "public_key": self.public_key,  # pylint: disable=no-member
                "locale_name": self.request.locale_name,
            }
        )
        return MappingWidget.serialize(self, field, cstruct, **kw)

    def deserialize(self, field: deform.field.Field, pstruct: JSONDict) -> Union[str, colander._null]:
        if pstruct is colander.null:
            return colander.null

        # get the verification token that is inserted into a hidden input
        # field created by the reCaptcha script. the value is available in
        # `pstruct` because we are inheriting from `MappingWidget`.
        response = pstruct.get("g-recaptcha-response") or ""
        if not response:
            raise Invalid(field.schema, _("Please verify that you are a human!"), pstruct)
        assert self.request is not None
        remoteip = self.request.remote_addr

        try:
            resp = requests.get(
                self.url,
                params={
                    "secret": self.private_key,  # pylint: disable=no-member
                    "response": response,
                    "remoteip": remoteip,
                },
                timeout=30,
            )
        except requests.exceptions.RequestException as exception:
            log.exception("reCaptcha connection problem")
            raise Invalid(field.schema, _("Connection problem"), pstruct) from exception
        if resp.status_code >= 500:
            log.error("reCaptcha connection problem (%i): %s", resp.status_code, resp.text)
            raise Invalid(field.schema, _("Connection problem"), pstruct)

        error_msg = _("Verification has failed")
        if not resp.status_code == 200:
            log.error("reCaptcha validation error: %s", resp.status_code)
            raise Invalid(field.schema, error_msg, pstruct)

        data = resp.json()
        if not data["success"]:
            error_reason = ""
            if "error-codes" in data:
                error_reason = ",".join(data["error-codes"])
            log.error("reCaptcha validation error: %s", error_reason)
            raise Invalid(field.schema, error_msg, pstruct)

        return pstruct
