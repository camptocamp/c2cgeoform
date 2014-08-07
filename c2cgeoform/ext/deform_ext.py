from translationstring import TranslationStringFactory
from deform.widget import (
    Widget, SelectWidget, Select2Widget, RadioChoiceWidget)
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
        isMultiGeometry = False

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
            isMultiGeometry = True

        return json.dumps({
            'point': point,
            'line': line,
            'polygon': polygon,
            'isMultiGeometry': isMultiGeometry,
            'readonly': readonly
        })


class RelationSelectMixin(object):

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


class RelationSelectWidget(RelationSelectMixin, SelectWidget):
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

    For further attributes, please refer to the documentation of
    ``deform.widget.SelectWidget`` in the deform documentation:
    <http://deform.readthedocs.org/en/latest/api.html>

    """

    def __init__(
            self, model, id_field, label_field,
            default_value=None, order_by=None, **kw):
        RelationSelectMixin.__init__(
            self, model, id_field, label_field, default_value, order_by)
        SelectWidget.__init__(self, **kw)


class RelationSelect2Widget(RelationSelectMixin, Select2Widget):
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

    For further attributes, please refer to the documentation of
    ``deform.widget.Select2Widget`` in the deform documentation:
    <http://deform.readthedocs.org/en/latest/api.html>

    """

    def __init__(
            self, model, id_field, label_field,
            default_value=None, order_by=None, **kw):
        RelationSelectMixin.__init__(
            self, model, id_field, label_field, default_value, order_by)
        Select2Widget.__init__(self, **kw)


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
