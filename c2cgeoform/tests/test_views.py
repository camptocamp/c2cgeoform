import unittest
import os
from pyramid import testing
from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config

from c2cgeoform.models import (DBSession, Base)


class TestView(unittest.TestCase):
    def setUp(self):
        curdir = os.path.dirname(os.path.abspath(__file__))
        configfile = os.path.realpath(
            os.path.join(curdir, '../../development.ini'))
        settings = get_appsettings(configfile)
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)

        from models_test import Person  # noqa
        Base.metadata.create_all(engine)
        self.cleanup()

    def tearDown(self):
        self.cleanup()

        DBSession.remove()
        testing.tearDown()

    def cleanup(self):
        from models_test import Person
        DBSession.query(Person).delete()

    def test_form_unknown_schema(self):
        from c2cgeoform.views import form
        request = testing.DummyRequest()
        request.matchdict['schema'] = 'unknown-schema'

        self.assertRaisesRegexp(
            RuntimeError, 'invalid schema \'unknown-schema\'',
            form, request)

    def test_form_show(self):
        from c2cgeoform.views import form
        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        response = form(request)

        self.assertTrue('form' in response)
        form_html = response['form']

        self.assertTrue('name="id"' in form_html)
        self.assertTrue('name="name"' in form_html)
        self.assertTrue('name="firstName"' in form_html)
        self.assertTrue('name="age"' in form_html)
        self.assertTrue('name="validated"' not in form_html)

    def test_form_submit_invalid(self):
        from c2cgeoform.views import form
        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        request.POST['submit'] = 'submit'
        response = form(request)

        self.assertTrue('form' in response)
        form_html = response['form']

        self.assertTrue('class="errorMsgLbl"' in form_html)

    def test_form_submit_successful(self):
        from c2cgeoform.views import form
        from models_test import Person

        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        request.POST['submit'] = 'submit'
        request.POST['name'] = 'Peter'
        request.POST['firstName'] = 'Smith'
        response = form(request)

        person = DBSession.query(Person).one()
        self.assertEquals('Peter', person.name)
        self.assertEquals('Smith', person.firstName)
        id = person.id

        self.assertTrue('form' in response)
        form_html = response['form']
        self.assertTrue('name="id"' in form_html)
        self.assertTrue('value="' + str(id) + '"' in form_html)
        self.assertTrue('name="submit"' not in form_html)

    def test_list(self):
        from c2cgeoform.views import list
        from models_test import Person
        DBSession.add(Person(name="Peter", firstName="Smith"))
        DBSession.add(Person(name="John", firstName="Wayne"))

        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        response = list(request)

        self.assertTrue('entities' in response)
        entities = response['entities']
        self.assertEquals(2, len(entities))

    def test_edit_show(self):
        from c2cgeoform.views import edit
        from models_test import Person
        person = Person(name="Peter", firstName="Smith")
        DBSession.add(person)
        DBSession.flush()

        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['id'] = str(person.id)
        response = edit(request)

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('name="id"' in form_html)
        self.assertTrue('value="' + str(person.id) + '"' in form_html)
        self.assertTrue('value="Peter"' in form_html)
        self.assertTrue('value="Smith"' in form_html)
        self.assertTrue('name="submit"' in form_html)

    def test_edit_submit_invalid(self):
        from c2cgeoform.views import edit
        from models_test import Person
        person = Person(name="Peter", firstName="Smith")
        DBSession.add(person)
        DBSession.flush()

        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['id'] = str(person.id)
        request.POST['id'] = str(person.id)
        request.POST['submit'] = 'submit'
        response = edit(request)

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('class="errorMsgLbl"' in form_html)

    def test_edit_submit_successful(self):
        from c2cgeoform.views import edit
        from models_test import Person
        person = Person(name="Peter", firstName="Smith")
        DBSession.add(person)
        DBSession.flush()

        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['id'] = str(person.id)
        request.POST['submit'] = 'submit'
        request.POST['id'] = str(person.id)
        request.POST['name'] = 'Peter'
        request.POST['firstName'] = 'Smith'
        request.POST['age'] = '43'
        response = edit(request)

        person = DBSession.query(Person).get(person.id)
        self.assertEquals('Peter', person.name)
        self.assertEquals('Smith', person.firstName)
        self.assertEquals(43, person.age)

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('name="id"' in form_html)
        self.assertTrue('value="' + str(person.id) + '"' in form_html)
        self.assertTrue('name="submit"' in form_html)
