from functools import partial
from itertools import groupby
from unittest import TestCase
from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from c2cgeoform.models import DBSession
from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.tests import DatabaseTestCase
from c2cgeoform.tests.models_test import Person, Tag
from c2cgeoform.views.abstract_views import AbstractViews, ListField

_list_field = partial(ListField, Person)


def get_rendered_form(response):
    return response["form"].render(*response["form_render_args"], **response["form_render_kwargs"])


class TestListField(TestCase):
    def test_title_default_to_attr_key(self):
        assert "id" == ListField(Tag, "id").label()


class ConcreteViews(AbstractViews):
    _model = Person
    _id_field = "id"
    _list_fields = [_list_field("name", label="Name"), _list_field("first_name")]
    _base_schema = GeoFormSchemaNode(Person, title="Person")


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
        self.request.route_url = Mock(return_value="person/new")
        views = ConcreteViews(self.request)
        response = views.index()
        assert "list_fields" in response

    def test_grid(self):
        self.request.route_url = Mock(return_value="person/1")
        self._add_test_persons()

        self.request.params["offset"] = "0"
        self.request.params["limit"] = "5"

        views = ConcreteViews(self.request)
        response = views.grid()

        assert 22 == response["total"]

        rows = response["rows"]
        assert 5 == len(rows)
        assert "_id_" in rows[0]
        assert "Smith" == rows[0]["name"]
        assert "person/1" == rows[0]["actions"]["dblclick"]
        call_list = self.request.route_url.call_args_list
        idx = [call[1]["id"] for call in call_list]
        grouped_by_id = [len(list(cgen)) for dummy, cgen in groupby(idx)]
        grouped_by_count = [len(list(cgen)) for dummy, cgen in groupby(grouped_by_id)]
        assert 1 == len(grouped_by_count)
        assert 5 == grouped_by_count[0]

    def test_grid_without_parameters(self):
        self.request.route_url = Mock(return_value="person/1")
        self._add_test_persons()
        views = ConcreteViews(self.request)
        response = views.grid()
        assert 22 == response["total"]

    def test_grid_with_nan(self):
        self.request.route_url = Mock(return_value="person/1")
        self._add_test_persons()
        self.request.params["offset"] = "NaN"
        self.request.params["limit"] = "NaN"
        views = ConcreteViews(self.request)
        response = views.grid()
        assert 22 == response["total"]

    def test_new_get(self):
        self.request.matched_route = Mock(name="c2cgeoform_item")
        self.request.route_url = Mock(return_value="person/new/edit")

        self.request.matchdict = {"id": "new"}
        views = ConcreteViews(self.request)
        response = views.edit()

        assert "form" in response
        assert "deform_dependencies" in response

    def test_new_post_validation_error(self):
        self.request.matched_route = Mock(name="c2cgeoform_item")
        self.request.route_url = Mock(return_value="person/new/save")

        self.request.matchdict = {"id": "new"}
        self.request.POST["first_name"] = "arnaud"
        self.request.POST["age"] = "37"

        views = ConcreteViews(self.request)
        response = views.save()

        assert "form" in response
        assert "deform_dependencies" in response

    def test_new_post_success(self):
        self.request.matched_route = Mock(name="person_action")
        self.request.route_url = Mock(return_value="person/new/save")
        self.request.dbsession.merge = Mock(
            return_value=Person(name="...", first_name="..."), age="...", id=7869
        )
        self.request.dbsession.flush = Mock()

        self.request.matchdict = {"id": "new"}
        self.request.POST["name"] = "morvan"
        self.request.POST["first_name"] = "arnaud"
        self.request.POST["age"] = "37"

        views = ConcreteViews(self.request)
        response = views.save()

        assert isinstance(response, HTTPFound)

        class Matcher:
            def __eq__(self, other):
                return other.name == "morvan" and other.first_name == "arnaud" and other.age == 37

        self.request.dbsession.merge.assert_called_with(Matcher())
        self.request.dbsession.flush.assert_called_once_with()

    def test_edit_get_not_found(self):
        self.request.matched_route = Mock(name="person_action")
        self.request.matchdict = {"id": 99999}
        self.request.route_url = Mock(return_value="person/99999")

        views = ConcreteViews(self.request)
        with pytest.raises(HTTPNotFound):
            views.edit()

    def test_edit_get_success(self):
        self._add_test_persons()
        self.request.matched_route = Mock(name="person_action")
        self.request.matchdict = {"id": self.person1.id}
        self.request.route_url = Mock(return_value="person/1")

        views = ConcreteViews(self.request)
        response = views.edit()

        assert "form" in response
        assert "deform_dependencies" in response

    def test_edit_post_notfound(self):
        self.request.matched_route = Mock(name="person_action")
        self.request.matchdict = {"id": 99999}
        self.request.route_url = Mock(return_value="person/99999")
        self.request.method = "POST"

        views = ConcreteViews(self.request)
        with pytest.raises(HTTPNotFound):
            views.save()

    def test_duplicate_get(self):
        self._add_test_persons()
        self.request.matched_route = Mock(name="c2cgeoform_item_action")
        self.request.matchdict = {"id": self.person1.id}
        self.request.route_url = Mock(return_value="c2cgeoform_item/new")
        self.request.method = "GET"

        views = ConcreteViews(self.request)
        response = views.duplicate()

        assert "form" in response
        assert "deform_dependencies" in response
        form = BeautifulSoup(get_rendered_form(response), "html.parser")
        # self.assertEqual('', form.select_one('form').attrs['action'])
        assert "" == form.select_one("input[name=id]").attrs["value"]
        assert self.person1.name == form.select_one("input[name=name]").attrs["value"]
        assert self.person1.first_name == form.select_one("input[name=first_name]").attrs["value"]
        assert "" == form.select_one("input[name=age]").attrs["value"]

    def test_copy_and_discard_excluded(self):
        self._add_test_persons()
        self.request.matched_route = Mock(name="c2cgeoform_item_action")
        self.request.matchdict = {"id": self.person1.id}
        self.request.route_url = Mock(return_value="c2cgeoform_item/new")
        self.request.method = "GET"
        person2 = self.request.dbsession.query(Person).filter(Person.name == "Wayne").one_or_none()
        views = ConcreteViews(self.request)

        response = views.copy(person2)
        form = BeautifulSoup(get_rendered_form(response), "html.parser")

        assert person2.name == form.select_one("input[name=name]").attrs["value"]
        assert person2.first_name == form.select_one("input[name=first_name]").attrs["value"]
        assert "" == form.select_one("input[name=age]").attrs["value"]

        response = views.copy(person2, ["first_name"])
        form = BeautifulSoup(get_rendered_form(response), "html.parser")

        assert person2.name == form.select_one("input[name=name]").attrs["value"]
        assert "" == form.select_one("input[name=first_name]").attrs["value"]
        assert "" == form.select_one("input[name=age]").attrs["value"]

    def test_delete(self):
        dbsession = self.request.dbsession

        self._add_test_persons()
        self.request.matched_route = Mock(name="person_action")
        self.request.matchdict = {"id": self.person1.id}
        self.request.route_url = Mock(return_value="person")
        dbsession.delete = Mock()
        flush_which_has_to_be_back_for_teardown = dbsession.flush
        try:
            dbsession.flush = Mock()

            views = ConcreteViews(self.request)
            response = views.delete()

            class Matcher:
                def __init__(self, person) -> None:
                    self.id = person.id

                def __eq__(self, other):
                    return other.id == self.id

            assert True is response["success"]
            assert "person" == response["redirect"]
            dbsession.delete.assert_called_once_with(Matcher(self.person1))
            dbsession.flush.assert_called_once_with()
        finally:
            dbsession.flush = flush_which_has_to_be_back_for_teardown
