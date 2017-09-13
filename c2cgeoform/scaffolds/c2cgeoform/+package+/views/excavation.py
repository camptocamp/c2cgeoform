from colanderalchemy import SQLAlchemySchemaNode
from pyramid.view import view_config

from c2cgeoform.views.abstract_views import AbstractViews

from ..models import Excavation


class ExcavationViews(AbstractViews):

    _model = Excavation
    _list_fields = [
        'reference_number',
        'request_date'
    ]
    _base_schema = SQLAlchemySchemaNode(Excavation, title='Person')

    @view_config(route_name='c2cgeoform_index',
                 match_param=('table=excavation'),
                 renderer='c2cgeoform:templates/site/index.pt')
    def index(self):
        return super().index()

    @view_config(route_name='c2cgeoform_grid',
                 match_param=('table=excavation'),
                 renderer='json')
    def grid(self):
        return super().grid()

    @view_config(route_name='c2cgeoform_new',
                 match_param=('table=excavation'),
                 renderer='c2cgeoform:templates/site/new.pt')
    def new(self):
        return super().new()
