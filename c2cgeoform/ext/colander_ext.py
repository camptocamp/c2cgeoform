
from colander import (null, Invalid)

from c2cgeoform.models import DBSession

from geoalchemy2 import WKBElement, functions
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import mapping, shape
import json


class Geometry(object):
    """
    """
    def __init__(self, geometry_type='GEOMETRY', srid=-1, map_srid=-1):
        self.geometry_type = geometry_type.upper()
        self.srid = int(srid)
        self.map_srid = int(map_srid)

    def serialize(self, node, appstruct):
        """
        In Colander speak: Converts a Python data structure (an appstruct) into
        a serialization (a cstruct).
        Or: Converts a `WKBElement` into a GeoJSON string.
        """
        if appstruct is null:
            return null
        if isinstance(appstruct, WKBElement):
            wkb = appstruct
            if self.srid != self.map_srid and wkb.srid != self.map_srid:
                wkb = DBSession.scalar(
                    functions.ST_Transform(wkb, self.map_srid))

            geometry = to_shape(wkb)
            return json.dumps(mapping(geometry))
        raise Invalid(node, 'Unexpected value: %r' % appstruct)

    def deserialize(self, node, cstruct):
        """
        In Colander speak: Converts a serialized value (a cstruct) into a
        Python data structure (a appstruct).
        Or: Converts a GeoJSON string into a `WKBElement`.
        """
        if cstruct is null or cstruct == '':
            return null
        try:
            geometry = from_shape(
                shape(json.loads(cstruct)),
                srid=self.map_srid)
        except Exception:
            raise Invalid(node, 'Invalid geometry: %r' % cstruct)

        if self.srid != self.map_srid:
            geometry = DBSession.scalar(
                functions.ST_Transform(geometry, self.srid))
            geometry = WKBElement(geometry.data, srid=self.srid)

        return geometry

    def cstruct_children(self, node, cstruct):
        return []
