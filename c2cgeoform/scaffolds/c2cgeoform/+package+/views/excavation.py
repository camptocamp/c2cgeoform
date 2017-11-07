from pyramid.view import view_config
from pyramid.view import view_defaults

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews
from ..models import Excavation


@view_defaults(match_param='table=excavations')
class ExcavationViews(AbstractViews):

    _model = Excavation
    _list_fields = [
        'reference_number',
        'request_date',
        'description',
        'location_town',
        'responsible_company',
    ]
    _base_schema = GeoFormSchemaNode(Excavation, title='Person')
    _id_field = 'hash'

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
