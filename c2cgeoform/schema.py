from functools import partial
from typing import Any, Optional, cast

import colander
import pyramid.request
import sqlalchemy.orm
import sqlalchemy.sql.elements
from colanderalchemy import SQLAlchemySchemaNode
from sqlalchemy import and_, or_
from sqlalchemy.inspection import inspect

from c2cgeoform import JSONDict, _


@colander.deferred  # type: ignore[misc]
def deferred_request(node: Any, kwargs: dict[str, Any]) -> pyramid.request.Request:
    del node  # unused
    return kwargs.get("request")


@colander.deferred  # type: ignore[misc]
def deferred_dbsession(node: Any, kwargs: dict[str, Any]) -> sqlalchemy.orm.Session:
    del node  # unused
    return cast(sqlalchemy.orm.Session, kwargs.get("dbsession"))


def unique_validator(
    mapper: type[Any],
    column: sqlalchemy.orm.attributes.InstrumentedAttribute[Any],
    id_column: sqlalchemy.orm.attributes.InstrumentedAttribute[Any],
    node: str,
    value: Any,
) -> None:
    dbsession: sqlalchemy.orm.Session = node.bindings["dbsession"]  # type: ignore[attr-defined]
    _id = node.bindings["request"].matchdict["id"]  # type: ignore[attr-defined]
    _id = _id if _id != "new" else None
    if dbsession.query(mapper).filter(column == value, id_column != _id).count() != 0:
        raise colander.Invalid(node, _("{} is already used.").format(value))


class GeoFormSchemaNode(SQLAlchemySchemaNode):  # type: ignore[misc] # pylint: disable=abstract-method
    """
    An SQLAlchemySchemaNode with deferred request and dbsession properties.
    This will allow defining schemas that requires the request and dbsession at
    module-scope.

    Example usage:

    .. code-block:: python

        schema = GeoFormSchemaNode(MyModel)

        def create_form(request, dbsession):
            return Form(
                schema = schema.bind(
                    request=request,
                    dbsession=request.dbsession),
                ...
            )
    """

    def __init__(self, *args: Any, **kw: Any) -> None:
        super().__init__(*args, **kw)
        self.request = deferred_request
        self.dbsession = deferred_dbsession

    def add_unique_validator(
        self,
        column: sqlalchemy.orm.attributes.InstrumentedAttribute[Any],
        column_id: sqlalchemy.orm.attributes.InstrumentedAttribute[Any],
    ) -> None:
        """
        Adds an unique validator on this schema instance.

        column
            SQLAlchemy ColumnProperty that should be unique.

        column_id
            SQLAlchemy MapperProperty that is used to recognize the entity,
            basically the primary key ColumnProperty.
        """
        validator = partial(unique_validator, self.class_, column, column_id)
        if self[column.name].validator is None:
            self[column.name].validator = validator
        else:
            self[column.name].validator = colander.All(self[column.name].validator, validator)


class GeoFormManyToManySchemaNode(GeoFormSchemaNode):  # pylint: disable=abstract-method
    """
    A GeoFormSchemaNode that properly handles many to many relationships.

    includes:
        Default to primary key name(s) only.
    """

    def __init__(self, class_: type[Any], includes: Optional[list[str]], *args: Any, **kw: Any) -> None:
        includes = [pk.name for pk in inspect(class_).primary_key]
        super().__init__(class_, includes, *args, **kw)

    def objectify(self, dict_: JSONDict, context: Any = None) -> Any:
        """
        Method override that returns the existing ORM class instance instead of
        creating a new one.
        """
        dbsession = self.bindings["dbsession"]
        class_ = self.inspector.class_
        return dbsession.query(class_).get(dict_.values())


def manytomany_validator(node: type[Any], cstruct: list[JSONDict]) -> None:
    """
    Validator function that checks if ``cstruct`` values exist in the related table.

    Note that entities are retrieved using only one query and placed in
    SQLAlchemy identity map before looping on ``cstruct``.
    """
    dbsession = node.bindings["dbsession"]
    class_ = node.children[0].inspector.class_
    query = dbsession.query(class_)
    filters = []
    for dict_ in cstruct:
        filters.append(and_(*[getattr(class_, key) == value for key, value in dict_.items()]))
    query = query.filter(or_(*filters))
    results = query.all()  # get all records in cache in one request
    diff = {tuple(dict_.values()) for dict_ in cstruct} - {inspect(a).identity for a in results}
    if len(diff) > 0:
        raise colander.Invalid(
            "Values {} does not exist in table {}".format(
                ", ".join(str(identity) for identity in diff), class_.__tablename__
            )
        )
