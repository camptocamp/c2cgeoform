from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from webob.multidict import MultiDict

from c2cgeoform.tests import DatabaseTestCase
from c2cgeoform.models import DBSession


class TestView(DatabaseTestCase):

    def test_form_unknown_schema(self):
        from c2cgeoform.views import form
        request = testing.DummyRequest()
        request.matchdict['schema'] = 'unknown-schema'

        self.assertRaisesRegexp(
            HTTPNotFound, 'invalid schema \'unknown-schema\'',
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

        request = testing.DummyRequest(post=MultiDict())
        request.matchdict['schema'] = 'tests_persons'
        request.POST.add('submit', 'submit')
        request.POST.add('name', 'Peter')
        request.POST.add('firstName', 'Smith')

        request.POST.add('__start__', 'phones:sequence')
        request.POST.add('__start__', 'phones:mapping')
        request.POST.add('id', '')
        request.POST.add('number', '123456789')
        request.POST.add('personId', '')
        request.POST.add('__end__', 'phones:mapping')
        request.POST.add('__end__', 'phones:sequence')

        response = form(request)

        person = DBSession.query(Person).one()
        self.assertEquals('Peter', person.name)
        self.assertEquals('Smith', person.firstName)
        self.assertEquals(1, len(person.phones))
        phone = person.phones[0]
        self.assertEquals('123456789', phone.number)
        self.assertIsNotNone(phone.id)

        id = person.id
        phone_id = phone.id

        self.assertTrue('form' in response)
        form_html = response['form']
        self.assertTrue('name="id" value="' + str(id) + '"' in form_html)
        self.assertTrue('name="id" value="' + str(phone_id) + '"' in form_html)
        self.assertTrue('name="personId" value="' + str(id) + '"' in form_html)
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
        from models_test import Person, Phone
        person = Person(name="Peter", firstName="Smith")
        phone = Phone(number="123456789")
        person.phones.append(phone)
        DBSession.add(person)
        DBSession.flush()

        request = testing.DummyRequest(post=MultiDict())
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['id'] = str(person.id)
        request.POST.add('id', str(person.id))
        request.POST.add('submit', 'submit')
        request.POST.add('name', 'Peter')
        request.POST.add('firstName', 'Smith')
        request.POST.add('age', '43')

        request.POST.add('__start__', 'phones:sequence')
        request.POST.add('__start__', 'phones:mapping')
        request.POST.add('id', str(phone.id))
        request.POST.add('number', '23456789')
        request.POST.add('personId', str(person.id))
        request.POST.add('__end__', 'phones:mapping')
        request.POST.add('__end__', 'phones:sequence')

        response = edit(request)

        person = DBSession.query(Person).get(person.id)
        self.assertEquals('Peter', person.name)
        self.assertEquals('Smith', person.firstName)
        self.assertEquals(43, person.age)
        self.assertEquals(1, len(person.phones))
        newPhone = person.phones[0]
        self.assertEquals('23456789', newPhone.number)
        self.assertEquals(phone.id, newPhone.id)

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('name="id"' in form_html)
        self.assertTrue('value="' + str(person.id) + '"' in form_html)
        self.assertTrue(
            'name="id" value="' + str(person.id) + '"' in form_html)
        self.assertTrue('name="id" value="' + str(phone.id) + '"' in form_html)
        self.assertTrue(
            'name="personId" value="' + str(person.id) + '"' in form_html)
        self.assertTrue('name="submit"' in form_html)

    def test_view(self):
        from c2cgeoform.views import view
        from models_test import Person
        person = Person(name="Peter", firstName="Smith")
        DBSession.add(person)
        DBSession.flush()

        request = testing.DummyRequest()
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['id'] = str(person.id)
        response = view(request)

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('name="id"' in form_html)
        self.assertTrue('value="' + str(person.id) + '"' in form_html)
        self.assertTrue('Peter' in form_html)
        self.assertTrue('Smith' in form_html)
