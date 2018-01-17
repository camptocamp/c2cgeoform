from functools import partial
import colander
from colanderalchemy import SQLAlchemySchemaNode
from sqlalchemy import and_, or_
from sqlalchemy.inspection import inspect
from c2cgeoform import _


@colander.deferred
def deferred_request(node, kw):
    return kw.get('request')


@colander.deferred
def deferred_dbsession(node, kw):
    return kw.get('dbsession')


def unique_validator(mapper, column, id_column, node, value):
    dbsession = node.bindings['dbsession']
    _id = node.bindings['request'].matchdict['id']
    _id = _id if _id != 'new' else None
    if dbsession.query(mapper).filter(column == value, id_column != _id).count() != 0:
        raise colander.Invalid(node, _('{} is already used.').format(value))


class GeoFormSchemaNode(SQLAlchemySchemaNode):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.request = deferred_request
        self.dbsession = deferred_dbsession

    def add_unique_validator(self, column, column_id):
        validator = partial(unique_validator, self.class_, column, column_id)
        if self[column.name].validator is None:
            self[column.name].validator = validator
        else:
            self[column.name].validator = colander.All(self[column.name].validator, validator)


class GeoFormManyToManySchemaNode(GeoFormSchemaNode):

    def __init__(self, class_, includes=None, *args, **kw):
        includes = [pk.name for pk in inspect(class_).primary_key]
        super().__init__(class_, includes, *args, **kw)

    def objectify(self, dict_, context=None):
        dbsession = self.bindings['dbsession']
        class_ = self.inspector.class_
        return dbsession.query(class_).get(dict_.values())


def manytomany_validator(node, cstruct):
    """
    Validate that cstruct values exists in related table.
    Note that entities are retrieved using only one query and placed in
    sqlalchemy identity map.
    """
    dbsession = node.bindings['dbsession']
    class_ = node.children[0].inspector.class_
    query = dbsession.query(class_)
    filters = []
    for dict_ in cstruct:
        filters.append(and_(*[getattr(class_, key) == value
                              for key, value in dict_.items()]))
    query = query.filter(or_(*filters))
    results = query.all()  # get all records in cache in one request
    diff = (set(tuple(dict_.values()) for dict_ in cstruct) -
            set([inspect(a).identity for a in results]))
    if len(diff) > 0:
        raise colander.Invalid(
            'Values {} does not exist in table {}'.
            format(", ".join(str(identity) for identity in diff),
                   class_.__tablename__))
