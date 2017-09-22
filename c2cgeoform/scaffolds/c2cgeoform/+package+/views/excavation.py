from colanderalchemy import SQLAlchemySchemaNode
from pyramid.view import view_config

from c2cgeoform.views.abstract_views import AbstractViews

from ..models import Excavation


class ExcavationViews(AbstractViews):

    _model = Excavation
    _list_fields = [
        'reference_number',
        'request_date',
        'description',
        'location_town',
        'responsible_company',
    ]
    _base_schema = SQLAlchemySchemaNode(Excavation, title='Person')
    _id_field = 'hash'

    @view_config(route_name='c2cgeoform_index',
                 match_param=('table=excavation'),
                 renderer='../templates/index.pt')
    def index(self):
        return super().index()

    @view_config(route_name='c2cgeoform_grid',
                 match_param=('table=excavation'),
                 renderer='json')
    def grid(self):
        return super().grid()

    @view_config(route_name='c2cgeoform_action',
                 match_param=('table=excavation', 'action=edit', 'id=new'),
                 renderer='../templates/new.pt')
    def new(self):
        return super().edit()

    @view_config(route_name='c2cgeoform_action',
                 match_param=('table=excavation', 'action=edit'),
                 request_method='GET',
                 renderer='c2cgeoform:templates/site/edit.pt')
    def edit(self):
        return super().edit()

    @view_config(route_name='c2cgeoform_action',
                 match_param=('table=excavation', 'action=edit'),
                 request_method='POST',
                 renderer='c2cgeoform:templates/site/edit.pt')
    def save(self):
        return super().save()
