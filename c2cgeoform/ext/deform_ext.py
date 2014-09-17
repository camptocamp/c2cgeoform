from translationstring import TranslationStringFactory
from deform.widget import Widget
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
