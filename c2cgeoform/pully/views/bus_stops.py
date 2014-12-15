from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from c2cgeoform.models import DBSession

from ..model import BusStop


def bus_stops(request):
    stops = DBSession.query(BusStop).all()
    return {
        'type': 'FeatureCollection',
        'features': [{
                'type': 'Feature',
                'id': stop.id,
                'properties': {
                    'name': stop.name},
                'geometry': mapping(to_shape(stop.geom))
        } for stop in stops]
    }
