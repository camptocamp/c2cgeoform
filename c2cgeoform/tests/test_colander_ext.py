import unittest
from colander import (null, Invalid)
from geoalchemy2 import WKBElement


class TestColanderExt(unittest.TestCase):

    def test_serialize_null(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        self.assertEquals(null, geomSchema.serialize({}, null))

    def test_serialize_wkb(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        from shapely.geometry.point import Point
        wkb = WKBElement(Point(1.0, 2.0).wkb)
        self.assertEquals(
            '{"type": "Point", "coordinates": [1.0, 2.0]}',
            geomSchema.serialize({}, wkb))

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

    def test_deserialize_valid_geojson(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geomSchema = Geometry()

        from shapely.geometry.point import Point
        expected_wkb = WKBElement(Point(1.0, 2.0).wkb)

        wkb = geomSchema.deserialize(
            {}, '{"type": "Point", "coordinates": [1.0, 2.0]}')
        self.assertEquals(expected_wkb.desc, wkb.desc)

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
