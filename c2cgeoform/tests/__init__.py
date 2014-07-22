import os
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config

from c2cgeoform.models import (DBSession, Base)


def setUp():
    curdir = os.path.dirname(os.path.abspath(__file__))
    configfile = os.path.realpath(
        os.path.join(curdir, '../../development.ini'))
    settings = get_appsettings(configfile)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    from models_test import Person  # noqa
    Base.metadata.create_all(engine)
    cleanup()


def tearDown():
    cleanup()
    DBSession.remove()


def cleanup():
    from models_test import Person
    DBSession.query(Person).delete()
