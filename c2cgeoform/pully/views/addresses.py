from pyramid.httpexceptions import HTTPBadRequest
from c2cgeoform.models import DBSession
from ..model import Address


def addresses(request):
    if 'term' not in request.params:
        return HTTPBadRequest()
    term = '%%%s%%' % request.params['term']
    query = DBSession.query(Address).filter(Address.label.ilike(term))
    return [{'id': addr.id, 'label': addr.label} for addr in query]
