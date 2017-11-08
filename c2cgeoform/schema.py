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
        if isinstance(dict_, self.inspector.class_):
            return dict_
        return super().objectify(dict_, context)


def manytomany_validator(node, cstruct):
    dbsession = node.bindings['dbsession']
    class_ = node.children[0].inspector.class_
    for i, dict_ in enumerate(cstruct):
        query = dbsession.query(class_)
        for key, value in dict_.items():
            query = query.filter(getattr(class_, key) == value)
        entity = query.one_or_none()
        if entity is None:
            raise colander.Invalid(
                '{} id={} does not exist'.
                format(class_.__name__, dict_['id']))
        else:
            cstruct[i] = entity
