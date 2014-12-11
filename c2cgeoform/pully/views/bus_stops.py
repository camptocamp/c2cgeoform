from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from c2cgeoform.models import DBSession

from c2cgeoform.pully.model import BusStop


def bus_stops(request):
    stops = DBSession.query(BusStop).all()
    return {
        'type': 'FeatureCollection',
        'features': [{
                'type': 'Feature',
                'properties': {
                    'id': stop.id,
                    'name': stop.name},
                'geometry': mapping(to_shape(stop.geom))
        } for stop in stops]
    }
