from pyramid.view import view_config
from pyramid.view import view_defaults
from functools import partial

from sqlalchemy.orm import subqueryload

import colander
from c2cgeoform.schema import (
    GeoFormSchemaNode,
    GeoFormManyToManySchemaNode,
    manytomany_validator,
)
from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from ..models.c2cgeoform_demo import Excavation, Situation

_list_field = partial(ListField, Excavation)

base_schema = GeoFormSchemaNode(Excavation)
base_schema.add_before(
    'contact_persons',
    colander.SequenceSchema(
        GeoFormManyToManySchemaNode(Situation),
        name='situations',
        title='Situations',
        widget=RelationCheckBoxListWidget(
            Situation,
            'id',
            'name',
            order_by='name'
        ),
        validator=manytomany_validator
    )
)


@view_defaults(match_param='table=excavations')
class ExcavationViews(AbstractViews):

    _model = Excavation

    _list_fields = [
        _list_field('reference_number'),
        _list_field('request_date'),
        _list_field('description'),
        _list_field('location_town'),
        _list_field('responsible_company'),
        _list_field('situations',
                    renderer=lambda excavation: ", ".join(
                        [s.name for s in excavation.situations]),
                    filter_column=Situation.name)
    ]

    _id_field = 'hash'
    _base_schema = base_schema

    def _base_query(self):
        return self._request.dbsession.query(Excavation).distinct(). \
            join('situations'). \
            options(subqueryload('situations'))

    @view_config(route_name='c2cgeoform_index',
                 renderer='../templates/index.jinja2')
    def index(self):
        return super().index()

    @view_config(route_name='c2cgeoform_grid',
                 renderer='json')
    def grid(self):
        return super().grid()

    @view_config(route_name='c2cgeoform_action',
                 request_method='GET',
                 renderer='../templates/new.jinja2')
    def edit(self):
        return super().edit()

    @view_config(route_name='c2cgeoform_action',
                 request_method='DELETE')
    def delete(self):
        return super().delete()

    @view_config(route_name='c2cgeoform_action',
                 request_method='POST',
                 renderer='../templates/edit.jinja2')
    def save(self):
        return super().save()
