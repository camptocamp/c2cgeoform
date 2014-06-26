from deform.widget import Widget
from colander import null
import cgi

class MapWidget(Widget):
    def serialize(self, field, cstruct, readonly=False, **kw):
        if cstruct is null:
            cstruct = u''
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer('map', **values)

    def deserialize(self, field, pstruct):
        return pstruct