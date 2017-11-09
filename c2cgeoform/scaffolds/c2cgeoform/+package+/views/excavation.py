from pyramid.view import view_config
from pyramid.view import view_defaults

import colander
from c2cgeoform.schema import (
    GeoFormSchemaNode,
    GeoFormManyToManySchemaNode,
    manytomany_validator,
)
from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from ..models.c2cgeoform_demo import Excavation, Situation


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
        ListField('reference_number'),
        ListField('request_date'),
        ListField('description'),
        ListField('location_town'),
        ListField('responsible_company'),
        ListField('situations',
                  renderer=lambda excavation:
                  ", ".join([s.name for s in excavation.situations]))
    ]
    _id_field = 'hash'
    _base_schema = base_schema

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
