from colander import null

from geoalchemy2 import WKTElement


class Geometry(object):
    def serialize(self, node, appstruct):
        if appstruct is null:
            return null
        return 'geometry'

    def deserialize(self, node, cstruct):
        if cstruct is null:
            return null
        return WKTElement('POINT(1 2)')
