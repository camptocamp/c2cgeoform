import colander
from colanderalchemy import SQLAlchemySchemaNode


@colander.deferred
def deferred_request(node, kw):
    return kw.get('request')


@colander.deferred
def deferred_dbsession(node, kw):
    return kw.get('dbsession')


class GeoFormSchemaNode(SQLAlchemySchemaNode):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.request = deferred_request
        self.dbsession = deferred_dbsession

    def objectify(self, dict_, context=None):
        context = super().objectify(dict_, context)
        return self.dbsession.merge(context)
