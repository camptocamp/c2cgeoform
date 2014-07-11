from colander import (null, Invalid)

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import mapping, shape
import json


class Geometry(object):
    """
    """
    def __init__(self, geometry_type='GEOMETRY', srid=-1):
        self.geometry_type = geometry_type.upper()
        self.srid = int(srid)

    def serialize(self, node, appstruct):
        """
        In Colander speak: Converts a Python data structure (an appstruct) into
        a serialization (a cstruct).
        Or: Converts a `WKBElement` into a GeoJSON string.
        """
        if appstruct is null:
            return null
        if isinstance(appstruct, WKBElement):
            geometry = to_shape(appstruct)
            return json.dumps(mapping(geometry))
        raise Invalid(node, 'Unexpected value: %r' % appstruct)

    def deserialize(self, node, cstruct):
        """
        In Colander speak: Converts a serialized value (a cstruct) into a
        Python data structure (a appstruct).
        Or: Converts a GeoJSON string into a `WKBElement`.
        """
        if cstruct is null:
            return null
        try:
            geometry = shape(json.loads(cstruct))
        except Exception:
            raise Invalid(node, 'Invalid geometry: %r' % cstruct)
        return from_shape(geometry)
