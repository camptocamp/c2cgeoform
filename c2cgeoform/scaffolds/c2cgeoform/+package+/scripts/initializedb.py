# coding=utf-8
import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    Base,
    DBSession,
    Address,
    District,
    Situation,
    BusStop,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        setup_test_data


def setup_test_data():
    if DBSession.query(District).count() == 0:
        DBSession.add(District(id=0, name="Pully"))
        DBSession.add(District(id=1, name="Paudex"))
        DBSession.add(District(id=2, name="Belmont-sur-Lausanne"))
        DBSession.add(District(id=3, name="Trois-Chasseurs"))
        DBSession.add(District(id=4, name="La Claie-aux-Moines"))
        DBSession.add(District(id=5, name="Savigny"))
        DBSession.add(District(id=6, name="Mollie-Margot"))

    if DBSession.query(Situation).count() == 0:
        DBSession.add(Situation(id=0, name="Road", name_fr="Route"))
        DBSession.add(Situation(id=1, name="Sidewalk", name_fr="Trottoir"))
        DBSession.add(Situation(id=2, name="Berm", name_fr="Berme"))
        DBSession.add(Situation(
            id=3, name="Vegetated berm", name_fr=u"Berme végétalisée"))
        DBSession.add(Situation(id=4, name="Green zone", name_fr="Zone verte"))
        DBSession.add(Situation(id=5, name="Cobblestone", name_fr="Pavés"))

    if DBSession.query(BusStop).count() == 0:
        _add_bus_stops()

    if DBSession.query(Address).count() == 0:
        DBSession.add(Address(id=0, label="Bern"))
        DBSession.add(Address(id=1, label="Lausanne"))
        DBSession.add(Address(id=2, label="Genève"))
        DBSession.add(Address(id=3, label="Zurich"))
        DBSession.add(Address(id=4, label="Lugano"))


def _add_bus_stops():
    """
    Load test data from a GeoJSON file.
    """
    import json
    from shapely.geometry import shape

    file = open(os.path.join(os.path.dirname(__file__),
                             '..',
                             'data',
                             'osm-lausanne-bus-stops.geojson'))
    geojson = json.load(file)
    file.close()

    bus_stops = []
    for feature in geojson['features']:
        id = feature['id'].replace('node/', '')
        geometry = shape(feature['geometry'])
        name = feature['properties']['name'] \
            if 'name' in feature['properties'] else ''
        bus_stop = BusStop(
            id=int(float(id)),
            geom='SRID=4326;' + geometry.wkt,
            name=name)
        bus_stops.append(bus_stop)

    DBSession.add_all(bus_stops)
