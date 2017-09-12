from colander import (null, Invalid)
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape, from_shape
import json

from c2cgeoform.tests import DatabaseTestCase


class TestGeometry(DatabaseTestCase):

    def test_serialize_null(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry()

        self.assertEquals(null, geom_schema.serialize({}, null))

    def test_serialize_wkb(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry()

        from shapely.geometry.point import Point
        wkb = from_shape(Point(1.0, 2.0))
        self.assertEquals(
            {"type": "Point", "coordinates": [1.0, 2.0]},
            json.loads(geom_schema.serialize({}, wkb)))

    def test_serialize_reproject(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry(srid=4326, map_srid=3857)

        from shapely.geometry.point import Point
        wkb = from_shape(Point(1.0, 2.0), 4326)
        geo_json = json.loads(geom_schema.serialize({}, wkb))
        self.assertEquals('Point', geo_json['type'])
        self.assertAlmostEqual(111319.49079327231, geo_json['coordinates'][0])
        self.assertAlmostEqual(222684.20850554455, geo_json['coordinates'][1])

    def test_serialize_invalid(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry()

        self.assertRaises(
            Invalid,
            geom_schema.serialize, {}, 'Point(1 0)')

    def test_deserialize_null(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry()

        self.assertEquals(null, geom_schema.deserialize({}, null))
        self.assertEquals(null, geom_schema.deserialize({}, ''))

    def test_deserialize_valid_geojson(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry()

        from shapely.geometry.point import Point
        expected_wkb = WKBElement(Point(1.0, 2.0).wkb)

        wkb = geom_schema.deserialize(
            {}, '{"type": "Point", "coordinates": [1.0, 2.0]}')
        self.assertEquals(expected_wkb.desc, wkb.desc)

    def test_deserialize_reproject(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry(srid=4326, map_srid=3857)

        wkb = geom_schema.deserialize(
            {},
            '{"type": "Point", '
            '"coordinates": [111319.49079327231, 222684.20850554455]}')
        self.assertEquals(4326, wkb.srid)

        shape = to_shape(wkb)
        self.assertAlmostEqual(1.0, shape.x)
        self.assertAlmostEqual(2.0, shape.y)

    def test_serialize_invalid_wrong_type(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry()

        self.assertRaises(
            Invalid,
            geom_schema.deserialize,
            {},
            '{"type": "InvalidType", "coordinates": [1.0, 2.0]}')

    def test_serialize_invalid_syntax(self):
        from c2cgeoform.ext.colander_ext import Geometry
        geom_schema = Geometry()

        self.assertRaises(
            Invalid,
            geom_schema.deserialize,
            {},
            '"type": "Point", "coordinates": [1.0, 2.0]}')


class TestBinaryData(DatabaseTestCase):

    def test_serialize_anything(self):
        from c2cgeoform.ext.colander_ext import BinaryData
        binary = BinaryData()
        serialized = binary.serialize({}, 'a string of binary data')
        self.assertNotEquals(null, serialized)
        self.assertEquals('a string of binary data', serialized.getvalue())

    def test_serialize_null(self):
        from c2cgeoform.ext.colander_ext import BinaryData
        binary = BinaryData()
        self.assertEquals(null, binary.serialize({}, null))

    def test_serialize_empty_string(self):
        from c2cgeoform.ext.colander_ext import BinaryData
        binary = BinaryData()
        self.assertEquals(null, binary.serialize({}, ''))

    def test_deserialize_null(self):
        from c2cgeoform.ext.colander_ext import BinaryData
        binary = BinaryData()
        self.assertEquals(null, binary.deserialize({}, null))

    def test_deserialize_empty_string(self):
        from c2cgeoform.ext.colander_ext import BinaryData
        binary = BinaryData()
        self.assertEquals(null, binary.deserialize({}, ''))

    def test_deserialize_file(self):
        import os
        from c2cgeoform.ext.colander_ext import BinaryData
        dirpath = os.path.dirname(os.path.realpath(__file__))
        file_ = open(os.path.join(dirpath, 'data', '1x1.png'), 'br')
        binary = BinaryData()
        self.assertIsInstance(binary.deserialize({}, file_), memoryview)

        # test that the file can be read multiple times (simulates that
        # a file in the tmpstore is requested several times)
        self.assertEquals(95, len(binary.deserialize({}, file_)))
        self.assertEquals(95, len(binary.deserialize({}, file_)))
        self.assertEquals(95, len(binary.deserialize({}, file_)))
