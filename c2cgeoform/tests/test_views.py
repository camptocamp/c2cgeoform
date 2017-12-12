from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import re

from c2cgeoform.tests import DatabaseTestCase
from c2cgeoform.models import DBSession


class TestView(DatabaseTestCase):

    BASE_URL = 'http://example.com/tests_persons'

    def _get_request(self):
        request = self.request

        # add a dummy `save` method to the session
        def save():
            pass
        request.session.save = save

        return request

    def test_form_unknown_schema(self):
        from c2cgeoform.views import form
        request = self._get_request()
        request.matchdict['schema'] = 'unknown-schema'

        self.assertRaisesRegexp(
            HTTPNotFound, 'invalid schema \'unknown-schema\'',
            form, request)

    def test_form_show(self):
        from c2cgeoform.views import form
        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        response = form(request)

        self.assertTrue('form' in response)
        form_html = response['form']

        self.assertTrue('name="id"' in form_html)
        self.assertTrue('name="name"' in form_html)
        self.assertTrue('name="first_name"' in form_html)
        self.assertTrue('name="age"' in form_html)
        self.assertTrue('name="validated"' not in form_html)
        self.assertTrue('verified' not in form_html)

        # check that the `overrides_user` property is used
        self.assertTrue('The Name' in form_html)

    def test_form_submit_invalid(self):
        from c2cgeoform.views import form
        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST['submit'] = 'submit'
        response = form(request)

        self.assertTrue('form' in response)
        form_html = response['form']

        self.assertTrue('class="errorMsgLbl"' in form_html)

    def test_form_submit_successful(self):
        from c2cgeoform.views import form, confirmation
        from models_test import Person

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST.add('submit', 'submit')
        request.POST.add('name', 'Peter')
        request.POST.add('first_name', 'Smith')

        request.POST.add('__start__', 'phones:sequence')
        request.POST.add('__start__', 'phones:mapping')
        request.POST.add('id', '')
        request.POST.add('number', '123456789')
        request.POST.add('personId', '')
        request.POST.add('__end__', 'phones:mapping')
        request.POST.add('__end__', 'phones:sequence')

        request.POST.add('__start__', 'tags:sequence')
        request.POST.add('tags', u'0')
        request.POST.add('tags', u'1')
        request.POST.add('__end__', 'tags:sequence')

        response = form(request)

        # valid submission, confirmation page should be shown
        self.assertTrue(isinstance(response, HTTPFound))
        url = TestView.BASE_URL + '/form/confirm?__submission_id__='
        self.assertTrue(response.location.startswith(url))

        # get submission_id
        matcher = re.search('__submission_id__=(.*)', response.location)
        submission_id = matcher.group(1)

        # simulate that the confirmation page is shown
        request2 = self._get_request()
        request2.session = request.session
        request2.matchdict['schema'] = 'tests_persons'
        request2.params['__submission_id__'] = submission_id

        response = confirmation(request2)
        self.assertTrue('form' in response)
        form_html = response['form']
        self.assertTrue(
            '<input type="hidden" name="__submission_id__"' in form_html)
        self.assertTrue(
            '<input type="hidden" name="__store_form__"' in form_html)

        # now simulate that the confirmation page is submitted
        request3 = self._get_request()
        request3.session = request.session
        request3.matchdict['schema'] = 'tests_persons'
        request3.params['__submission_id__'] = submission_id
        request3.params['__store_form__'] = '1'

        response = confirmation(request3)

        person = DBSession.query(Person).one()
        self.assertIsNotNone(person.hash)
        self.assertEquals('Peter', person.name)
        self.assertEquals('Smith', person.first_name)
        self.assertEquals(1, len(person.phones))
        phone = person.phones[0]
        self.assertEquals('123456789', phone.number)
        self.assertIsNotNone(phone.id)
        self.assertEquals(2, len(person.tags))
        tag_for_person1 = person.tags[0]
        self.assertEquals(0, tag_for_person1.tag_id)
        self.assertEquals(person.id, tag_for_person1.person_id)
        self.assertIsNotNone(tag_for_person1.id)
        tag_for_person2 = person.tags[1]
        self.assertEquals(1, tag_for_person2.tag_id)
        self.assertEquals(person.id, tag_for_person2.person_id)
        self.assertIsNotNone(tag_for_person2.id)

        self.assertTrue(isinstance(response, HTTPFound))
        self.assertEquals(
            TestView.BASE_URL + '/form/' + person.hash,
            response.location)

    def test_form_submit_successful_without_confirmation(self):
        from c2cgeoform.views import form, confirmation
        from c2cgeoform.schema import register_schema
        from models_test import Person
        register_schema(
            'tests_persons_no_confirmation', Person,
            show_confirmation=False)

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons_no_confirmation'
        request.POST.add('submit', 'submit')
        request.POST.add('name', 'Peter')
        request.POST.add('first_name', 'Smith')

        request.POST.add('__start__', 'phones:sequence')
        request.POST.add('__start__', 'phones:mapping')
        request.POST.add('id', '')
        request.POST.add('number', '123456789')
        request.POST.add('personId', '')
        request.POST.add('__end__', 'phones:mapping')
        request.POST.add('__end__', 'phones:sequence')

        request.POST.add('__start__', 'tags:sequence')
        request.POST.add('tags', u'0')
        request.POST.add('tags', u'1')
        request.POST.add('__end__', 'tags:sequence')

        response = form(request)

        # valid submission, redirect to confirmation view
        self.assertTrue(isinstance(response, HTTPFound))
        url = TestView.BASE_URL + '_no_confirmation' + \
            '/form/confirm?__submission_id__='
        self.assertTrue(response.location.startswith(url))

        # get submission_id
        matcher = re.search('__submission_id__=(.*)', response.location)
        submission_id = matcher.group(1)

        # simulate that the confirmation view is called,
        # which directly persists the object
        request2 = self._get_request()
        request2.session = request.session
        request2.matchdict['schema'] = 'tests_persons_no_confirmation'
        request2.params['__submission_id__'] = submission_id

        response = confirmation(request2)

        person = DBSession.query(Person).one()
        self.assertIsNotNone(person.hash)
        self.assertEquals('Peter', person.name)
        self.assertEquals('Smith', person.first_name)
        self.assertEquals(1, len(person.phones))
        phone = person.phones[0]
        self.assertEquals('123456789', phone.number)
        self.assertIsNotNone(phone.id)
        self.assertEquals(2, len(person.tags))
        tag_for_person1 = person.tags[0]
        self.assertEquals(0, tag_for_person1.tag_id)
        self.assertEquals(person.id, tag_for_person1.person_id)
        self.assertIsNotNone(tag_for_person1.id)
        tag_for_person2 = person.tags[1]
        self.assertEquals(1, tag_for_person2.tag_id)
        self.assertEquals(person.id, tag_for_person2.person_id)
        self.assertIsNotNone(tag_for_person2.id)

        self.assertTrue(isinstance(response, HTTPFound))
        self.assertEquals(
            TestView.BASE_URL + '_no_confirmation' + '/form/' + person.hash,
            response.location)

    def test_form_submit_confirmation_back(self):
        from c2cgeoform.views import form
        from models_test import Person

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST.add('submit', 'submit')
        request.POST.add('name', 'Peter')
        request.POST.add('first_name', 'Smith')

        response = form(request)

        # valid submission, confirmation page should be shown
        self.assertTrue(isinstance(response, HTTPFound))
        url = TestView.BASE_URL + '/form/confirm?__submission_id__='
        self.assertTrue(response.location.startswith(url))

        # get submission_id
        matcher = re.search('__submission_id__=(.*)', response.location)
        submission_id = matcher.group(1)

        # now simulate going back to the form
        request2 = self._get_request()
        request2.session = request.session
        request2.matchdict['schema'] = 'tests_persons'
        request2.params['__submission_id__'] = submission_id

        response = form(request2)
        form_html = response['form']
        # form is shown again with values restored from the session
        self.assertTrue(
            '<input type="text" name="name" value="Peter"' in form_html)

        # and no row was created
        count = DBSession.query(Person).count()
        self.assertEquals(0, count)

    def test_form_submit_only_validate(self):
        from c2cgeoform.views import form
        from models_test import Person

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST.add('submit', 'submit')
        request.POST.add('name', 'Peter')
        request.POST.add('first_name', 'Smith')
        request.POST.add('__only_validate__', '1')

        form(request)
        count = DBSession.query(Person).count()

        # form was valid, but no row was created
        self.assertEquals(0, count)

    def test_list(self):
        from c2cgeoform.views import list
        from models_test import Person
        DBSession.add(Person(name="Peter", first_name="Smith"))
        DBSession.add(Person(name="John", first_name="Wayne"))

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        response = list(request)

        self.assertTrue('entities' in response)
        entities = response['entities']
        self.assertEquals(2, len(entities))

        schema = response['schema']
        self.assertEquals(['id', 'name'], schema.list_fields)

    def test_grid(self):
        from c2cgeoform.views import grid
        _add_test_persons()

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST['current'] = '1'
        request.POST['rowCount'] = '5'
        response = grid(request)

        self.assertEquals(1, response['current'])
        self.assertEquals(5, response['rowCount'])
        self.assertEquals(22, response['total'])

        rows = response['rows']
        self.assertEquals(5, len(rows))
        self.assertTrue('_id_' in rows[0])
        self.assertEquals('Smith', rows[0]['name'])

    def test_grid_sort(self):
        from c2cgeoform.views import grid
        _add_test_persons()

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST['current'] = '1'
        request.POST['rowCount'] = '5'
        request.POST['sort[name]'] = 'asc'
        response = grid(request)

        self.assertEquals(1, response['current'])
        self.assertEquals(5, response['rowCount'])
        self.assertEquals(22, response['total'])

        rows = response['rows']
        self.assertEquals('Bess', rows[0]['name'])
        self.assertEquals('Claudio', rows[1]['name'])

    def test_grid_paging(self):
        from c2cgeoform.views import grid
        _add_test_persons()

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST['current'] = '2'
        request.POST['rowCount'] = '5'
        request.POST['sort[name]'] = 'asc'
        response = grid(request)

        self.assertEquals(2, response['current'])
        self.assertEquals(5, response['rowCount'])
        self.assertEquals(22, response['total'])

        rows = response['rows']
        self.assertEquals('Elda', rows[0]['name'])
        self.assertEquals('Eloise', rows[1]['name'])

        # invalid page
        request.POST['current'] = '99'
        response = grid(request)
        self.assertEquals(5, response['current'])

    def test_grid_search(self):
        from c2cgeoform.views import grid
        _add_test_persons()

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.POST['current'] = '1'
        request.POST['rowCount'] = '5'
        request.POST['sort[name]'] = 'asc'
        request.POST['searchPhrase'] = 'sha'
        response = grid(request)

        self.assertEquals(1, response['current'])
        self.assertEquals(5, response['rowCount'])
        self.assertEquals(4, response['total'])

        request.POST['searchPhrase'] = '   Smith  '
        response = grid(request)
        self.assertEquals(1, response['total'])

        request.POST['searchPhrase'] = 'NOT FOUND'
        response = grid(request)
        self.assertEquals(0, response['total'])

        request.POST['searchPhrase'] = 'Peter'
        response = grid(request)
        self.assertEquals(0, response['total'])

    def test_edit_show(self):
        from c2cgeoform.views import edit
        from models_test import Person
        person = Person(name="Peter", first_name="Smith")
        DBSession.add(person)
        DBSession.flush()

        request = self._get_request()
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
        person = Person(name="Peter", first_name="Smith")
        DBSession.add(person)
        DBSession.flush()

        request = self._get_request()
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
        from models_test import Person, Phone, TagsForPerson
        person = Person(name="Peter", first_name="Smith")
        phone = Phone(number="123456789")
        person.phones.append(phone)
        tag_for_person = TagsForPerson(tag_id=0)
        person.tags.append(tag_for_person)
        DBSession.add(person)
        DBSession.flush()
        old_tag_for_person_id = tag_for_person.id

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['id'] = str(person.id)
        request.POST.add('id', str(person.id))
        request.POST.add('submit', 'submit')
        request.POST.add('name', 'Peter')
        request.POST.add('first_name', 'Smith')
        request.POST.add('age', '43')

        request.POST.add('__start__', 'phones:sequence')
        request.POST.add('__start__', 'phones:mapping')
        request.POST.add('id', str(phone.id))
        request.POST.add('number', '23456789')
        request.POST.add('person_id', str(person.id))
        request.POST.add('__end__', 'phones:mapping')
        request.POST.add('__start__', 'phones:mapping')
        request.POST.add('number', '123456')
        request.POST.add('__end__', 'phones:mapping')
        request.POST.add('__end__', 'phones:sequence')

        request.POST.add('__start__', 'tags:sequence')
        request.POST.add('tags', u'0')
        request.POST.add('tags', u'1')
        request.POST.add('__end__', 'tags:sequence')

        response = edit(request)

        person = DBSession.query(Person).get(person.id)
        self.assertEquals('Peter', person.name)
        self.assertEquals('Smith', person.first_name)
        self.assertEquals(43, person.age)
        self.assertEquals(2, len(person.phones))
        updated_phone = person.phones[0]
        self.assertEquals('23456789', updated_phone.number)
        self.assertEquals(phone.id, updated_phone.id)
        new_phone = person.phones[1]
        self.assertEquals('123456', new_phone.number)
        self.assertIsNotNone(new_phone.id)
        self.assertEquals(2, len(person.tags))
        tag_for_person1 = person.tags[0]
        self.assertEquals(0, tag_for_person1.tag_id)
        self.assertEquals(person.id, tag_for_person1.person_id)
        self.assertIsNotNone(tag_for_person1.id)
        # a new row is created, also for the old entry
        self.assertNotEquals(old_tag_for_person_id, tag_for_person1.id)
        tag_for_person2 = person.tags[1]
        self.assertEquals(1, tag_for_person2.tag_id)
        self.assertEquals(person.id, tag_for_person2.person_id)
        self.assertIsNotNone(tag_for_person2.id)
        tags_for_persons = DBSession.query(TagsForPerson).all()
        # check that the old entry was deleted, so that there are only 2
        self.assertEquals(2, len(tags_for_persons))

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('name="id"' in form_html)
        self.assertTrue('value="' + str(person.id) + '"' in form_html)
        self.assertTrue(
            'name="id" value="' + str(person.id) + '"' in form_html)
        self.assertTrue('name="id" value="' + str(phone.id) + '"' in form_html)
        self.assertTrue(
            'name="id" value="' + str(new_phone.id) + '"' in form_html)
        self.assertTrue(
            'name="person_id" value="' + str(person.id) + '"' in form_html)
        self.assertTrue('name="submit"' in form_html)
        self.assertTrue('Tag A' in form_html)
        self.assertTrue('Tag B' in form_html)

    def test_view_user(self):
        from c2cgeoform.views import view_user
        from models_test import Person
        person = Person(name="Peter", first_name="Smith", hash="123-456")
        DBSession.add(person)
        DBSession.flush()

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['hash'] = "123-456"
        response = view_user(request)

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('Peter' in form_html)
        self.assertTrue('Smith' in form_html)

    def test_view_user_fail(self):
        from c2cgeoform.views import view_user

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        response = view_user(request)

        self.assertIsNone(response['form'])

    def test_view_admin(self):
        from c2cgeoform.views import view_admin
        from models_test import Person
        person = Person(name="Peter", first_name="Smith")
        DBSession.add(person)
        DBSession.flush()

        request = self._get_request()
        request.matchdict['schema'] = 'tests_persons'
        request.matchdict['id'] = str(person.id)
        response = view_admin(request)

        self.assertTrue('schema' in response)
        self.assertTrue('form' in response)

        form_html = response['form']
        self.assertTrue('name="id"' in form_html)
        self.assertTrue('value="' + str(person.id) + '"' in form_html)
        self.assertTrue('Peter' in form_html)
        self.assertTrue('Smith' in form_html)


def _add_test_persons():
    from models_test import Person
    DBSession.add(Person(name="Smith", first_name="Peter"))
    DBSession.add(Person(name="Wayne", first_name="John"))
    DBSession.add(Person(name="Elda", first_name="Hasbrouck"))
    DBSession.add(Person(name="Lashaun", first_name="Brasel"))
    DBSession.add(Person(name="Lashawna", first_name="Ashford"))
    DBSession.add(Person(name="Lesha", first_name="Snellgrove"))
    DBSession.add(Person(name="Sulema", first_name="Page"))
    DBSession.add(Person(name="Derek", first_name="Boroughs"))
    DBSession.add(Person(name="Odis", first_name="Bateman"))
    DBSession.add(Person(name="Venetta", first_name="Briganti"))
    DBSession.add(Person(name="Monte", first_name="Quill"))
    DBSession.add(Person(name="Daniel", first_name="Ruth"))
    DBSession.add(Person(name="Eloise", first_name="Hellickson"))
    DBSession.add(Person(name="Hee", first_name="Deloney"))
    DBSession.add(Person(name="Sharee", first_name="Warf"))
    DBSession.add(Person(name="Delpha", first_name="Philip"))
    DBSession.add(Person(name="Claudio", first_name="Campfield"))
    DBSession.add(Person(name="Janessa", first_name="Beatty"))
    DBSession.add(Person(name="Hollis", first_name="Richmond"))
    DBSession.add(Person(name="Karoline", first_name="Carew"))
    DBSession.add(Person(name="Bess", first_name="Papp"))
    DBSession.add(Person(name="Vada", first_name="Infantino"))
