import os
import time
import unittest

from pyramid import testing
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config, text
from webob.multidict import MultiDict

from c2cgeoform import init_deform
from c2cgeoform.models import Base, DBSession
from c2cgeoform.settings import apply_local_settings


def wait_for_db(engine):
    sleep_time = 1
    max_sleep = 30
    while sleep_time < max_sleep:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1;"))
            return
        except Exception as e:
            print(str(e))
            print("Waiting for the DataBase server to be reachable")
            time.sleep(sleep_time)
            sleep_time *= 2
    exit(1)  # noqa


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):  # noqa
        curdir = os.path.dirname(os.path.abspath(__file__))
        configfile = os.path.realpath(os.path.join(curdir, "../../tests.ini"))
        settings = get_appsettings(configfile)
        apply_local_settings(settings)
        engine = engine_from_config(settings, "sqlalchemy.")
        DBSession.configure(bind=engine)

        wait_for_db(engine)

        from .models_test import EmploymentStatus, Person, Tag  # noqa

        Base.metadata.create_all(engine)
        self.cleanup()

        # fill some test data into the `EmploymentStatus` and `Tags` table
        DBSession.add(EmploymentStatus(id=0, name="Worker"))
        DBSession.add(EmploymentStatus(id=1, name="Employee"))
        DBSession.add(EmploymentStatus(id=2, name="Self-employed and contractor"))
        DBSession.add(EmploymentStatus(id=3, name="Director"))
        DBSession.add(EmploymentStatus(id=4, name="Office holder"))

        DBSession.add(Tag(id=0, name="Tag A"))
        DBSession.add(Tag(id=1, name="Tag B"))
        DBSession.add(Tag(id=2, name="Tag C"))
        DBSession.add(Tag(id=3, name="Tag D"))
        DBSession.add(Tag(id=4, name="Tag E"))

        self.request = testing.DummyRequest(post=MultiDict(), dbsession=DBSession)
        testing.setUp(request=self.request)

        config = testing.setUp()
        config.add_route("form", "/{schema}/form/")
        config.add_route("view_user", "/{schema}/form/{hash}")
        config.add_route("confirm", "/{schema}/form/confirm")
        init_deform("c2cgeoform")

    def tearDown(self):  # noqa
        self.cleanup()
        DBSession.remove()
        testing.tearDown()

    def cleanup(self):
        from .models_test import EmploymentStatus, Person, Phone, Tag

        DBSession.query(Tag).delete()
        DBSession.query(Phone).delete()
        DBSession.query(Person).delete()
        DBSession.query(EmploymentStatus).delete()
