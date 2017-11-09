from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from unittest.mock import Mock

from c2cgeoform.models import DBSession
from c2cgeoform.tests import DatabaseTestCase
from c2cgeoform.tests.models_test import Person
from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews
from c2cgeoform.views.abstract_views import ListField


class ConcreteViews(AbstractViews):

    _model = Person
    _id_field = 'id'
    _list_fields = [ListField('name', label='Name'), ListField('first_name')]
    _base_schema = GeoFormSchemaNode(Person, title='Person')


class TestAbstractViews(DatabaseTestCase):

    def _add_test_persons(self):
        self.person1 = Person(name="Smith", first_name="Peter")
        DBSession.add(self.person1)
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
        DBSession.flush()

    def test_index(self):
        views = ConcreteViews(self.request)
        response = views.index()
        expected = {'list_fields':
                    [('name', 'Name'),
                     ('first_name', 'Your first name')]}
        self.assertEquals(expected, response)

    def test_grid(self):
        self._add_test_persons()

        self.request.params['current'] = '1'
        self.request.params['rowCount'] = '5'

        views = ConcreteViews(self.request)
        response = views.grid()

        self.assertEquals(1, response['current'])
        self.assertEquals(5, response['rowCount'])
        self.assertEquals(22, response['total'])

        rows = response['rows']
        self.assertEquals(5, len(rows))
        self.assertTrue('_id_' in rows[0])
        self.assertEquals('Smith', rows[0]['name'])

    def test_new_get(self):
        self.request.matched_route = Mock(name='c2cgeoform_action')
        self.request.route_url = Mock(return_value='person/new/edit')

        self.request.matchdict = {'id': 'new'}
        views = ConcreteViews(self.request)
        response = views.edit()

        self.assertIn('form', response)
        self.assertIn('deform_dependencies', response)

    def test_new_post_validation_error(self):
        self.request.matched_route = Mock(name='c2cgeoform_action')
        self.request.route_url = Mock(return_value='person/new/save')

        self.request.matchdict = {'id': 'new'}
        self.request.POST['first_name'] = 'arnaud'
        self.request.POST['age'] = '37'

        views = ConcreteViews(self.request)
        response = views.save()

        self.assertIn('form', response)
        self.assertIn('deform_dependencies', response)

    def test_new_post_success(self):
        self.request.matched_route = Mock(name='person_action')
        self.request.route_url = Mock(return_value='person/new/save')
        self.request.dbsession.merge = Mock(return_value=Person(
            name='...',
            first_name='...'),
            age='...',
            id=7869)
        self.request.dbsession.flush = Mock()

        self.request.matchdict = {'id': 'new'}
        self.request.POST['name'] = 'morvan'
        self.request.POST['first_name'] = 'arnaud'
        self.request.POST['age'] = '37'

        views = ConcreteViews(self.request)
        response = views.save()

        self.assertIsInstance(response, HTTPFound)

        class Matcher():
            def __eq__(self, other):
                return other.name == 'morvan' \
                    and other.first_name == 'arnaud' \
                    and other.age == 37
        self.request.dbsession.merge.assert_called_with(Matcher())
        self.request.dbsession.flush.assert_called_once_with()

    def test_edit_get_not_found(self):
        self.request.matched_route = Mock(name='person_action')
        self.request.matchdict = {'id': 99999}
        self.request.route_url = Mock(return_value='person/99999')

        views = ConcreteViews(self.request)
        with self.assertRaises(HTTPNotFound):
            views.edit()

    def test_edit_get_success(self):
        self._add_test_persons()
        self.request.matched_route = Mock(name='person_action')
        self.request.matchdict = {'id': self.person1.id}
        self.request.route_url = Mock(return_value='person/1')

        views = ConcreteViews(self.request)
        response = views.edit()

        self.assertIn('form', response)
        self.assertIn('deform_dependencies', response)

    def test_edit_post_notfound(self):
        self.request.matched_route = Mock(name='person_action')
        self.request.matchdict = {'id': 99999}
        self.request.route_url = Mock(return_value='person/99999')
        self.request.method = 'POST'

        views = ConcreteViews(self.request)
        with self.assertRaises(HTTPNotFound):
            views.save()

    def test_delete_person(self):
        dbsession = self.request.dbsession

        self._add_test_persons()
        self.request.matched_route = Mock(name='person_action')
        self.request.matchdict = {'id': self.person1.id}
        self.request.route_url = Mock(return_value='person/1')
        dbsession.delete = Mock()
        flush_which_has_to_be_back_for_teardown = dbsession.flush
        try:
            dbsession.flush = Mock()

            views = ConcreteViews(self.request)
            response = views.delete()

            class Matcher():
                def __init__(self, person):
                    self.id = person.id

                def __eq__(self, other):
                    return other.id == self.id
            self.assertEqual('OK', response.text)
            dbsession.delete.assert_called_once_with(Matcher(self.person1))
            dbsession.flush.assert_called_once_with()
        finally:
            dbsession.flush = flush_which_has_to_be_back_for_teardown
