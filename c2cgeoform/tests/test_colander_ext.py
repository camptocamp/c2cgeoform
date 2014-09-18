from colander import (null, Invalid)
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape, from_shape
import json

from c2cgeoform.tests import DatabaseTestCase


class TestColanderExt(DatabaseTestCase):

    def test_serialize_null(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        self.assertEquals(null, geomSchema.serialize({}, null))

    def test_serialize_wkb(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        from shapely.geometry.point import Point
        wkb = from_shape(Point(1.0, 2.0))
        self.assertEquals(
            '{"type": "Point", "coordinates": [1.0, 2.0]}',
            geomSchema.serialize({}, wkb))

    def test_serialize_reproject(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry(srid=4326, map_srid=3857)

        from shapely.geometry.point import Point
        wkb = from_shape(Point(1.0, 2.0), 4326)
        geoJson = json.loads(geomSchema.serialize({}, wkb))
        self.assertEquals('Point', geoJson['type'])
        self.assertAlmostEqual(111319.49079327231, geoJson['coordinates'][0])
        self.assertAlmostEqual(222684.20850554455, geoJson['coordinates'][1])

    def test_serialize_invalid(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        self.assertRaises(
            Invalid,
            geomSchema.serialize, {}, 'Point(1 0)')

    def test_deserialize_null(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        self.assertEquals(null, geomSchema.deserialize({}, null))
        self.assertEquals(null, geomSchema.deserialize({}, ''))

    def test_deserialize_valid_geojson(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        from shapely.geometry.point import Point
        expected_wkb = WKBElement(Point(1.0, 2.0).wkb)

        wkb = geomSchema.deserialize(
            {}, '{"type": "Point", "coordinates": [1.0, 2.0]}')
        self.assertEquals(expected_wkb.desc, wkb.desc)

    def test_deserialize_reproject(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry(srid=4326, map_srid=3857)

        wkb = geomSchema.deserialize(
            {},
            '{"type": "Point", '
            '"coordinates": [111319.49079327231, 222684.20850554455]}')
        self.assertEquals(4326, wkb.srid)

        shape = to_shape(wkb)
        self.assertAlmostEqual(1.0, shape.x)
        self.assertAlmostEqual(2.0, shape.y)

    def test_serialize_invalid_wrong_type(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        self.assertRaises(
            Invalid,
            geomSchema.deserialize,
            {},
            '{"type": "InvalidType", "coordinates": [1.0, 2.0]}')

    def test_serialize_invalid_syntax(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        self.assertRaises(
            Invalid,
            geomSchema.deserialize,
            {},
            '"type": "Point", "coordinates": [1.0, 2.0]}')
