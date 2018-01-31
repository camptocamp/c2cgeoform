import os
import unittest
from pyramid import testing
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config
from webob.multidict import MultiDict

from c2cgeoform.models import (DBSession, Base)
from c2cgeoform.settings import apply_local_settings
from c2cgeoform import init_deform


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):  # noqa
        curdir = os.path.dirname(os.path.abspath(__file__))
        configfile = os.path.realpath(
            os.path.join(curdir, '../../tests.ini'))
        settings = get_appsettings(configfile)
        apply_local_settings(settings)
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)

        from .models_test import Person, EmploymentStatus, Tag  # noqa
        Base.metadata.create_all(engine)
        self.cleanup()

        # fill some test data into the `EmploymentStatus` and `Tags` table
        DBSession.add(EmploymentStatus(id=0, name='Worker'))
        DBSession.add(EmploymentStatus(id=1, name='Employee'))
        DBSession.add(EmploymentStatus(
            id=2, name='Self-employed and contractor'))
        DBSession.add(EmploymentStatus(id=3, name='Director'))
        DBSession.add(EmploymentStatus(id=4, name='Office holder'))

        DBSession.add(Tag(id=0, name='Tag A'))
        DBSession.add(Tag(id=1, name='Tag B'))
        DBSession.add(Tag(id=2, name='Tag C'))
        DBSession.add(Tag(id=3, name='Tag D'))
        DBSession.add(Tag(id=4, name='Tag E'))

        self.request = testing.DummyRequest(post=MultiDict(),
                                            dbsession=DBSession)
        testing.setUp(request=self.request)

        config = testing.setUp()
        config.add_route('form', '/{schema}/form/')
        config.add_route('view_user', '/{schema}/form/{hash}')
        config.add_route('confirm', '/{schema}/form/confirm')
        init_deform('c2cgeoform')

    def tearDown(self):  # noqa
        self.cleanup()
        DBSession.remove()
        testing.tearDown()

    def cleanup(self):
        from .models_test import Person, EmploymentStatus, Phone, \
            Tag
        DBSession.query(Tag).delete()
        DBSession.query(Phone).delete()
        DBSession.query(Person).delete()
        DBSession.query(EmploymentStatus).delete()
