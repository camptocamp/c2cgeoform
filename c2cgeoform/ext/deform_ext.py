from translationstring import TranslationStringFactory
from deform.widget import (
    Widget, SelectWidget, Select2Widget, RadioChoiceWidget)
from deform.widget import FileUploadWidget as DeformFileUploadWidget
from sqlalchemy.orm import ColumnProperty
from colander import null
import json


class MapWidget(Widget):
    requirements = (
        ('openlayers', '3.0.0'),
        ('json2', None),
        ('c2cgeoform.deform_map', None),)

    def serialize(self, field, cstruct, readonly=False, **kw):
        if cstruct is null:
            cstruct = u''
        values = self.get_template_values(field, cstruct, kw)
        values['controls_definition'] = \
            self._get_controls_definition(field, readonly)
        # make `_` available in template for i18n messages
        values['_'] = TranslationStringFactory('c2cgeoform')
        return field.renderer('map', **values)

    def deserialize(self, field, pstruct):
        return pstruct

    def _get_controls_definition(self, field, readonly):
        geometry_type = field.typ.geometry_type

        point = True
        line = True
        polygon = True
        is_multi_geometry = False

        if 'POINT' in geometry_type:
            line = False
            polygon = False
        elif 'LINESTRING' in geometry_type:
            point = False
            polygon = False
        elif 'POLYGON' in geometry_type:
            point = False
            line = False

        if 'MULTI' in geometry_type \
                or geometry_type == 'GEOMETRY' \
                or geometry_type == 'GEOMETRYCOLLECTION':
            is_multi_geometry = True

        return json.dumps({
            'point': point,
            'line': line,
            'polygon': polygon,
            'isMultiGeometry': is_multi_geometry,
            'readonly': readonly
        })


class RelationSelectMixin(object):
    """
    Mixin class to support relations for select fields.
    """

    def __init__(
            self, model, id_field, label_field,
            default_value=None, order_by=None):
        self.model = model
        self.id_field = id_field
        self.label_field = label_field
        self.default_value = default_value
        self.order_by = order_by

    def populate(self, session):
        self.values = self._get_select_values(session)

    def _get_select_values(self, session):
        if self.order_by is not None:
            order_by = getattr(self.model, self.order_by)
        else:
            order_by = None

        entities = session.query(self.model).order_by(order_by).all()

        values = tuple(
            (getattr(entity, self.id_field), getattr(entity, self.label_field))
            for entity in entities)

        if self.default_value is None:
            return values
        else:
            return (self.default_value,) + values


class RelationMultiSelectMixin(RelationSelectMixin):
    """
    Mixin class to support n:m relations for select fields.
    """

    def deserialize(self, field, pstruct):
        """
        Deserialize the field input for a n:m relation.

        For example for a n:m relation between table A and B and a relation
        table A_B: Let's assume this widget is used in model A, so that
        you can select entries of B. Then this method will receive a list of
        ids of table B. For each id it will create an object containing the id.
        These objects will be inserted in the relation table A_B.
        """
        if pstruct in (null, None):
            return []
        ids = pstruct

        # get the id field of the mapped table B in the relation table A_B
        mapped_id_field = self._get_mapped_id_field(field)

        result = []
        for id in ids:
            # create an entry for the relation table A_B
            obj = {}
            # set the id for an entity of the mapped table B,
            # the id for an entity of table A will be filled in automatically
            obj[mapped_id_field.name] = mapped_id_field.deserialize(id)
            result.append(obj)

        return result

    def serialize(self, field, cstruct, **kw):
        """
        Flatten a list of objects into a list of ids.
        """
        mapped_id_field = self._get_mapped_id_field(field)
        # create a list with only the ids of entities of table B
        if cstruct in (null, None):
            cstruct = []
        return [obj[mapped_id_field.name] for obj in cstruct]

    def _get_mapped_id_field(self, field):
        """
        For the given relation field in table A, find the foreign key field
        for table B in the relation table A_B.
        """
        relation_field = field.children[0]

        relation_table = relation_field.schema.class_
        mapped_id_field_name = self._get_mapped_id_field_name(relation_table)

        # get the Deform field for the found foreign key column
        for subfield in relation_field.children:
            if subfield.name == mapped_id_field_name:
                return subfield

        raise RuntimeError(
            'The foreign key column for table "' + self.model.__table__.name +
            '" can not be found in the ' + 'relation table "' +
            relation_table.local_table.name + '" for field "' +
            field.name + '".')

    def _get_mapped_id_field_name(self, relation_table):
        """ Loop through the columns of the relation table A_B and
        find the foreign key for table B.
        """
        for mapped_column in relation_table.attrs:
            if isinstance(mapped_column, ColumnProperty):
                column = mapped_column.columns[0]
                foreign_keys = list(column.foreign_keys)
                for foreign_key in foreign_keys:
                    if foreign_key.column.table == self.model.__table__:
                        return column.name
        return None


class RelationSelectWidget(RelationMultiSelectMixin, SelectWidget):
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
            SituationForPermission,
            cascade="all, delete-orphan",
            info={
                'colanderalchemy': {
                    'title': 'Situation',
                    'widget': deform_ext.RelationSelectWidget(
                        Situation,
                        'id',
                        'name',
                        order_by='name',
                        multiple=True
                    )
                }})

    **Attributes/Arguments**

    model
        The SQLAlchemy model that is used to generate the list of values.

    id_field
        The property of the model that is used as value.

    label_field
        The property of the model that is used as label.

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
            self, model, id_field, label_field,
            default_value=None, order_by=None, **kw):
        RelationMultiSelectMixin.__init__(
            self, model, id_field, label_field, default_value, order_by)
        SelectWidget.__init__(self, **kw)

    def deserialize(self, field, pstruct):
        if self.multiple:
            return RelationMultiSelectMixin.deserialize(self, field, pstruct)
        else:
            return SelectWidget.deserialize(self, field, pstruct)

    def serialize(self, field, cstruct, **kw):
        if self.multiple:
            cstruct = RelationMultiSelectMixin.serialize(
                self, field, cstruct, **kw)
        return SelectWidget.serialize(self, field, cstruct, **kw)


class RelationSelect2Widget(RelationMultiSelectMixin, Select2Widget):
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
            SituationForPermission,
            cascade="all, delete-orphan",
            info={
                'colanderalchemy': {
                    'title': 'Situation',
                    'widget': deform_ext.RelationSelect2Widget(
                        Situation,
                        'id',
                        'name',
                        order_by='name',
                        multiple=True
                    )
                }})

    **Attributes/Arguments**

    model
        The SQLAlchemy model that is used to generate the list of values.

    id_field
        The property of the model that is used as value.

    label_field
        The property of the model that is used as label.

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
            self, model, id_field, label_field,
            default_value=None, order_by=None, **kw):
        RelationMultiSelectMixin.__init__(
            self, model, id_field, label_field, default_value, order_by)
        Select2Widget.__init__(self, **kw)

    def deserialize(self, field, pstruct):
        if self.multiple:
            return RelationMultiSelectMixin.deserialize(self, field, pstruct)
        else:
            return Select2Widget.deserialize(self, field, pstruct)

    def serialize(self, field, cstruct, **kw):
        if self.multiple:
            cstruct = RelationMultiSelectMixin.serialize(
                self, field, cstruct, **kw)
        return Select2Widget.serialize(self, field, cstruct, **kw)


class RelationRadioChoiceWidget(RelationSelectMixin, RadioChoiceWidget):
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

    model
        The SQLAlchemy model that is used to generate the list of values.

    id_field
        The property of the model that is used as value.

    label_field
        The property of the model that is used as label.

    order_by
        The property of the model that is used for the ``order_by`` clause of
        the SQL query.
        Default: ``None``.

    For further attributes, please refer to the documentation of
    ``deform.widget.RadioChoiceWidget`` in the deform documentation:
    <http://deform.readthedocs.org/en/latest/api.html>

    """

    def __init__(
            self, model, id_field, label_field, order_by=None, **kw):
        RelationSelectMixin.__init__(
            self, model, id_field, label_field, None, order_by)
        RadioChoiceWidget.__init__(self, **kw)


class FileUploadWidget(DeformFileUploadWidget):
    """ Extension of ``deform.widget.FileUploadWidget`` to be used in a model
    class that extends the ``models.FileData`` mixin class.

    Note: contrary to ``deform.widget.FileUploadWidget`` this extension is not
    meant to be used with the ``deform.FileData`` Colander type. Instead it
    works with the ``colander.Mapping`` type, which is what ``colanderalchemy``
    uses for an SQLAlchemy model class.

    Example usage

    .. code-block:: python

        from c2cgeoform import models
        from c2cgeoform.ext import deform_ext

        class Photo(models.FileData, Base):
            __tablename__ = 'photo'
            __colanderalchemy_config__ = {
                'title': _('Photo'),
                'widget': deform_ext.FileUploadWidget(file_upload_temp_store)
            }
            permission_id = Column(Integer, ForeignKey('excavations.id'))
    """

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = {}
        if 'id' in cstruct:
            cstruct['uid'] = cstruct['id']
        return DeformFileUploadWidget.serialize(self, field, cstruct, **kw)

    def deserialize(self, field, pstruct):
        value = DeformFileUploadWidget.deserialize(self, field, pstruct)
        if value != null and 'fp' in value:
            value['data'] = value['fp']
        return value
