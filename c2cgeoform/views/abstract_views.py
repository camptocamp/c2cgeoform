import logging
from typing import Any, Callable, Dict, Generic, Optional, Tuple, TypedDict, TypeVar, Union, cast

import geojson
import pyramid.request
import pyramid.response
import sqlalchemy.engine.row
import sqlalchemy.orm.attributes
import sqlalchemy.orm.properties
import sqlalchemy.schema
import sqlalchemy.sql.elements
import sqlalchemy.sql.expression
from deform import Form, ValidationFailure  # , ZPTRendererFactory
from deform.form import Button
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from geojson import Feature, FeatureCollection
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError, HTTPNotFound
from sqlalchemy import desc, or_, types
from sqlalchemy.exc import DBAPIError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from translationstring import TranslationString

from c2cgeoform import JSON, JSONDict, JSONList, _, default_map_settings

_LOGGER = logging.getLogger(__name__)

_DB_ERR_MSG = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_c2cgeoportal_admin_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


def model_attr_info(
    attr: Optional[
        Union[
            str,
            sqlalchemy.orm.attributes.InstrumentedAttribute[Any],
            sqlalchemy.orm.relationships.Relationship[Any],
            sqlalchemy.orm.relationships.RelationshipProperty[Any],
            sqlalchemy.sql.schema.Column[Any],
            sqlalchemy.sql.elements.NamedColumn[Any],
        ]
    ],
    *keys: str,
    default: Any = None,
) -> Any:
    if attr is None:
        return default

    assert isinstance(
        attr,
        (
            sqlalchemy.orm.attributes.InstrumentedAttribute,
            sqlalchemy.orm.relationships.Relationship,
            sqlalchemy.orm.relationships.RelationshipProperty,
            sqlalchemy.sql.schema.Column,
            sqlalchemy.sql.elements.NamedColumn,
        ),
    ), type(attr)
    value = attr.info
    for key in keys:
        if key not in value:
            return default
        value = value[key]
    return value


T = TypeVar("T", bound=type)


def _getattr(
    model: Optional[type[T]], attr: Optional[Union[sqlalchemy.schema.Column[Any], str]]
) -> sqlalchemy.schema.Column[Any]:
    if model is None:
        assert isinstance(attr, sqlalchemy.schema.Column)
        return attr
    assert isinstance(attr, str)
    return cast(sqlalchemy.schema.Column[Any], getattr(model, attr))


class ListField(Generic[T]):
    def __init__(
        self,
        model: Optional[type[T]] = None,
        attr: Optional[str] = None,
        key: Optional[str] = None,
        label: Optional[str] = None,
        renderer: Optional[Callable[[T], JSON]] = None,
        sort_column: Optional[sqlalchemy.sql.elements.ColumnElement[Any]] = None,
        filter_column: Optional[sqlalchemy.sql.elements.ColumnElement[Any]] = None,
        visible: bool = True,
    ):
        self._attr = _getattr(model, attr)
        self._key = key or self._attr.key
        self._label = label or model_attr_info(self._attr, "colanderalchemy", "title") or self._key
        self._renderer = renderer or self._prop_renderer
        is_column = isinstance(self._attr.property, ColumnProperty)
        self._sort_column = sort_column or (self._attr if is_column else None)
        self._filter_column = (
            filter_column if filter_column is not None else self._attr if is_column else None
        )
        self._visible = visible

    def _prop_renderer(self, entity: T) -> str:
        value = None
        if self._attr is not None:
            value = getattr(entity, self._attr.key)
        if value is None:
            return ""
        if isinstance(value, WKBElement):
            return "Geometry"
        return str(value)

    def id(self) -> Optional[str]:  # pylint: disable=invalid-name
        return self._key

    def label(self) -> str:
        return self._label

    def value(self, entity: T) -> JSON:
        return self._renderer(entity)

    def sortable(self) -> bool:
        return self._sort_column is not None

    def filtrable(self) -> bool:
        return self._filter_column is not None and isinstance(self._filter_column.type, types.String)

    def sort_column(self) -> sqlalchemy.sql.expression.ColumnElement[Any]:
        assert self._sort_column is not None
        return self._sort_column

    def filter_expression(self, term: str) -> sqlalchemy.sql.expression.BinaryExpression[bool]:
        assert self._filter_column is not None
        return self._filter_column.ilike(term)

    def visible(self) -> bool:
        return self._visible


class ItemAction:
    def __init__(
        self,
        name: str,
        url: str,
        method: Union[bool, str] = False,
        label: Optional[str] = None,
        css_class: str = "",
        icon: Optional[str] = None,
        confirmation: str = "",
    ) -> None:
        self._name = name
        self._url = url
        self._method = method
        self._label = label or self._name
        self._css_class = css_class
        self._icon = icon
        self._confirmation = confirmation

    def name(self) -> str:
        return self._name

    def url(self) -> str:
        return self._url

    def method(self) -> Union[bool, str]:
        return self._method

    def label(self) -> str:
        return self._label

    def css_class(self) -> str:
        return self._css_class

    def icon(self) -> Optional[str]:
        return self._icon

    def confirmation(self) -> str:
        return self._confirmation

    def to_dict(self, request: pyramid.request.Request) -> JSONDict:
        return {
            "name": self._name,
            "url": self._url,
            "method": self._method,
            "label": request.localizer.translate(self._label),
            "css_class": self._css_class,
            "icon": self._icon,
            "confirmation": self._confirmation,
        }


class UserMessage:
    def __init__(self, text: str, css_class: str = "alert-success") -> None:
        self._text = text
        self._css_class = css_class

    def text(self) -> str:
        return self._text

    def css_class(self) -> str:
        return self._css_class

    def __str__(self) -> str:
        # For compatibility with old templates
        return self._text


# TODO for Python 3.11
# class IndexResponse(TypedDict, Generic[T]):
#     grid_actions: list[ItemAction]
#     list_fields: list[ListField[T]]
class IndexResponse(TypedDict):
    grid_actions: list[ItemAction]
    list_fields: list[ListField[Any]]


class GridResponse(TypedDict):
    rows: JSONList
    total: int


class MapResponse(TypedDict):
    map_options: Dict[str, Any]


class DeformDependencies:
    css: Dict[str, str]
    js: Dict[str, str]


class ObjectResponse(TypedDict):
    title: str
    form: Form
    form_render_args: Union[tuple[Any], list[Any]]
    form_render_kwargs: dict[str, Any]
    deform_dependencies: DeformDependencies


SaveResponse = Union[HTTPFound, ObjectResponse]


class DeleteResponse(TypedDict):
    success: bool
    redirect: str


class AbstractViews(Generic[T]):
    _model: Optional[type[T]] = None  # sqlalchemy model
    _list_fields: list[ListField[T]] = []  # Fields in list
    _list_ordered_fields: list[
        Union[sqlalchemy.sql.elements.ColumnClause[Any], sqlalchemy.sql.elements.ColumnElement[Any]]
    ] = []  # Fields in list used for default orderby
    _id_field: Optional[str] = None  # Primary key
    _geometry_field: Optional[str] = None  # Geometry field
    _base_schema: Optional[type[T]] = None  # base colander schema

    MSG_COL = {
        "submit_ok": UserMessage(_("Your submission has been taken into account."), "alert-success"),
        "copy_ok": UserMessage(_("Please check that the copy fits before submitting."), "alert-info"),
    }

    def __init__(self, request: pyramid.request.Request) -> None:
        self._request = request
        self._schema: Optional[str] = None
        self._appstruct: Optional[Dict[str, Any]] = None
        self._obj: Optional[T] = None

    def index(self) -> IndexResponse:
        return {
            "grid_actions": self._grid_actions(),
            "list_fields": self._list_fields,
        }

    def grid(self) -> GridResponse:
        """
        API method which serves the JSON data for the Bootgrid table in the admin view.
        """
        try:
            params = self._request.params
            offset = int(params.get("offset", 0) if params.get("offset") != "NaN" else 0)
            limit = int(params.get("limit", -1) if params.get("limit") != "NaN" else -1)
            search = params.get("search", "").strip()
            sort = params.get("sort", "")
            order = params.get("order", "")

            query = self._base_query()
            query = self._filter_query(query, search)
            query = self._sort_query(query, sort, order)

            return {"rows": self._grid_rows(query, offset, limit), "total": query.count()}
        except DBAPIError as exception:
            _LOGGER.error(str(exception), exc_info=True)
            raise HTTPInternalServerError(_DB_ERR_MSG) from exception

    def map(self, map_settings: Optional[JSONDict] = None) -> MapResponse:
        map_settings = map_settings or {}
        map_options = {
            **default_map_settings,
            **{
                "url": self._request.route_url(
                    "c2cgeoform_geojson",
                    _query={
                        "srid": map_settings.get("srid", default_map_settings["srid"]),
                    },
                ),
            },
            **map_settings,
        }
        return {
            "map_options": {
                key: (self._request.translate(value) if isinstance(value, TranslationString) else value)
                for key, value in map_options.items()
            }
        }

    def geojson(self) -> geojson.FeatureCollection:
        assert self._geometry_field is not None
        assert self._id_field is not None

        srid = int(self._request.params.get("srid", 3857))

        query = self._base_query().add_column(
            getattr(self._model, self._geometry_field).ST_Transform(srid).label("_geometry")
        )

        features: list[geojson.Feature] = []
        for entities in query:
            entity = entities[0]
            geometry = entities[-1]
            features.append(
                Feature(
                    id=getattr(entity, self._id_field),
                    geometry=to_shape(geometry) if geometry is not None else None,
                    properties={f.id(): f.value(entity) for f in self._list_fields},
                )
            )
        return FeatureCollection(features)

    def _base_query(self) -> sqlalchemy.orm.query.Query[T]:
        return cast(sqlalchemy.orm.query.Query[T], self._request.dbsession.query(self._model))

    def _filter_query(
        self, query: sqlalchemy.orm.query.Query[T], search_phrase: str
    ) -> sqlalchemy.orm.query.Query[T]:
        if search_phrase != "":
            search_expr = "%" + "%".join(search_phrase.split()) + "%"

            # create `ilike` filters for every list text field
            filters = []
            for field in self._list_fields:
                if field.filtrable():
                    filters.append(field.filter_expression(search_expr))

            # then join the filters into one `or` condition
            if len(filters) > 0:
                query = query.filter(or_(*filters))

        return query

    def _sort_query(
        self, query: sqlalchemy.orm.query.Query[T], sort: str, order: str
    ) -> sqlalchemy.orm.query.Query[T]:
        for field in self._list_fields:
            if field.id() == sort:
                if order == "desc":
                    query = query.order_by(desc(field.sort_column()))
                else:
                    query = query.order_by(field.sort_column())
        # default order by
        for order_field in self._list_ordered_fields:
            query = query.order_by(order_field)
        return query

    def _grid_rows(self, query: sqlalchemy.orm.query.Query[T], offset: int, limit: int) -> JSONList:
        # Sort on primary key as subqueryload with limit need deterministic order
        for pkey_column in inspect(self._model).primary_key:  # type: ignore[union-attr]
            query = query.order_by(pkey_column)

        if limit != -1:
            query = query.limit(limit).offset(offset)
        rows: JSONList = []

        for entities in query:
            # For some reason like:
            # https://docs.sqlalchemy.org/en/14/changelog/migration_20.html#using-distinct-with-additional-columns-but-only-select-the-entity
            # we are required to add a second field to the query, in this case we should get only the first one
            entity: T = (
                cast(sqlalchemy.engine.row.Row[Tuple[T, Any]], entities)[0]
                if isinstance(entities, sqlalchemy.engine.row.Row)
                else entities
            )
            row = cast(
                JSONDict,
                {
                    f.id(): f.value(entity)
                    for f in (self._list_fields + [ListField(self._model, self._id_field, key="_id_")])
                },
            )
            row["actions"] = self._grid_item_actions(entity)
            rows.append(row)
        return rows

    def _form(self, schema: Optional[type[T]] = None, **kwargs: Any) -> Form:
        schema = schema or self._base_schema
        assert schema is not None
        self._schema = schema.bind(request=self._request, dbsession=self._request.dbsession)  # type: ignore[attr-defined]

        form = Form(self._schema, buttons=[Button(name="formsubmit", title=_("Submit"))], **kwargs)

        return form

    def _populate_widgets(self, node: Any) -> None:
        """Populate ``deform_ext.RelationSelectMixin`` widgets."""

        if hasattr(node.widget, "populate"):
            node.widget.populate(self._request.dbsession, self._request)

        for child in node:
            self._populate_widgets(child)

    def _is_new(self) -> bool:
        return self._request.matchdict.get("id") == "new"  # type: ignore[no-any-return]

    def _get_object(self) -> T:
        assert self._id_field is not None

        if self._is_new():
            assert self._model is not None
            return cast(T, self._model())  # type: ignore[call-overload] # pylint: disable=not-callable
        primary_key = self._request.matchdict.get("id")
        obj = (
            self._request.dbsession.query(self._model)
            .filter(getattr(self._model, self._id_field) == primary_key)
            .one_or_none()
        )
        if obj is None:
            raise HTTPNotFound()
        return cast(T, obj)

    def _model_config(self) -> JSONDict:
        return getattr(inspect(self._model).class_, "__c2cgeoform_config__", {})  # type: ignore[union-attr]

    def _grid_actions(self) -> list[ItemAction]:
        return [
            ItemAction(
                name="new",
                label=_("New"),
                css_class="btn btn-primary btn-new",
                url=self._request.route_url("c2cgeoform_item", id="new"),
            )
        ]

    def _grid_item_actions(self, item: T) -> JSONDict:
        assert self._id_field is not None

        actions = self._item_actions(item)
        actions.insert(
            0,
            ItemAction(
                name="edit",
                label=_("Edit"),
                icon="glyphicon glyphicon-pencil",
                url=self._request.route_url("c2cgeoform_item", id=getattr(item, self._id_field)),
            ),
        )
        return {
            "dropdown": [action.to_dict(self._request) for action in actions],
            "dblclick": self._request.route_url("c2cgeoform_item", id=getattr(item, self._id_field)),
        }

    def _item_actions(self, item: T, readonly: bool = False) -> list[ItemAction]:
        assert self._id_field is not None

        actions = []

        inspected_item: Any = inspect(item)
        assert isinstance(inspected_item, sqlalchemy.orm.InstanceState)
        if inspected_item.persistent and self._model_config().get("duplicate", False):
            actions.append(
                ItemAction(
                    name="duplicate",
                    label=_("Duplicate"),
                    icon="glyphicon glyphicon-duplicate",
                    url=self._request.route_url(
                        "c2cgeoform_item_duplicate", id=getattr(item, self._id_field)
                    ),
                )
            )

        if inspected_item.persistent and not readonly:
            actions.append(
                ItemAction(
                    name="delete",
                    label=_("Delete"),
                    icon="glyphicon glyphicon-remove",
                    url=self._request.route_url("c2cgeoform_item", id=getattr(item, self._id_field)),
                    method="DELETE",
                    confirmation=_("Are your sure you want to delete this record ?"),
                )
            )

        return actions

    def edit(self, schema: Optional[type[T]] = None, readonly: bool = False) -> ObjectResponse:
        obj = self._get_object()
        form = self._form(schema=schema, readonly=readonly)
        self._populate_widgets(form.schema)
        dict_ = form.schema.dictify(obj)
        if self._is_new():
            dict_.update(self._request.GET)
        kwargs = {
            "request": self._request,
            "actions": self._item_actions(obj, readonly=readonly),
            "readonly": readonly,
            "obj": obj,
        }
        if "msg_col" in self._request.params and self._request.params["msg_col"] in self.MSG_COL:
            msg = self.MSG_COL[self._request.params["msg_col"]]
            if isinstance(msg, str):
                # For compatibility with old views
                msg = UserMessage(msg, "alert-success")
            kwargs.update({"msg_col": [msg]})
        return {
            "title": form.title,
            "form": form,
            "form_render_args": (dict_,),
            "form_render_kwargs": kwargs,
            "deform_dependencies": form.get_widget_resources(),
        }

    def copy_members_if_duplicates(self, source: T, excludes: Optional[list[str]] = None) -> T:
        dest = cast(T, source.__class__())  # type: ignore[call-overload]
        insp = inspect(source.__class__)

        for prop in insp.attrs:  # type: ignore[union-attr]
            if isinstance(prop, ColumnProperty):
                is_primary_key = prop.columns[0].primary_key
                to_duplicate = model_attr_info(prop.columns[0], "c2cgeoform", "duplicate", default=True)
                to_exclude = excludes and prop.columns[0].key in excludes
                if not is_primary_key and to_duplicate and not to_exclude:
                    setattr(dest, prop.key, getattr(source, prop.key))
            if isinstance(prop, RelationshipProperty):
                if model_attr_info(prop, "c2cgeoform", "duplicate", default=True):
                    if prop.cascade.delete:
                        if not prop.uselist:
                            duplicate: Union[T, list[T]] = self.copy_members_if_duplicates(
                                getattr(source, prop.key)
                            )
                        else:
                            duplicate = [
                                self.copy_members_if_duplicates(m) for m in getattr(source, prop.key)
                            ]
                    else:
                        duplicate = getattr(source, prop.key)
                    setattr(dest, prop.key, duplicate)
        return dest

    def copy(self, src: T, excludes: Optional[list[str]] = None) -> ObjectResponse:
        # excludes only apply at first level
        form = self._form(action=self._request.route_url("c2cgeoform_item", id="new"))
        with self._request.dbsession.no_autoflush:
            dest = self.copy_members_if_duplicates(src, excludes)
            dict_ = form.schema.dictify(dest)
            if self._is_new():
                dict_.update(self._request.GET)
            if dest in self._request.dbsession:
                self._request.dbsession.expunge(dest)
                self._request.dbsession.expire_all()

        self._populate_widgets(form.schema)
        kwargs = {
            "request": self._request,
            "actions": self._item_actions(dest),
            "msg_col": [self.MSG_COL["copy_ok"]],
        }

        return {
            "title": form.title,
            "form": form,
            "form_render_args": (dict_,),
            "form_render_kwargs": kwargs,
            "deform_dependencies": form.get_widget_resources(),
        }

    def duplicate(self) -> ObjectResponse:
        src = self._get_object()
        return self.copy(src)

    def save(self) -> SaveResponse:
        obj = self._get_object()
        try:
            form = self._form()
            self._populate_widgets(form.schema)
            form_data = self._request.POST.items()
            self._appstruct = form.validate(form_data)
            with self._request.dbsession.no_autoflush:
                obj = form.schema.objectify(self._appstruct, obj)
            self._obj = self._request.dbsession.merge(obj)
            self._request.dbsession.flush()
            return HTTPFound(
                self._request.route_url(
                    "c2cgeoform_item",
                    action="edit",
                    id=self._obj.__getattribute__(self._id_field),  # type: ignore[arg-type] # pylint: disable=unnecessary-dunder-call
                    _query=[("msg_col", "submit_ok")],
                )
            )
        except ValidationFailure as exception:
            self._populate_widgets(form.schema)
            kwargs = {"request": self._request, "actions": self._item_actions(obj), "obj": obj}
            return {
                "title": form.title,
                "form": exception,
                "form_render_args": [],
                "form_render_kwargs": kwargs,
                "deform_dependencies": form.get_widget_resources(),
            }

    def delete(self) -> DeleteResponse:
        obj = self._get_object()
        self._request.dbsession.delete(obj)
        self._request.dbsession.flush()
        return {"success": True, "redirect": self._request.route_url("c2cgeoform_index")}
