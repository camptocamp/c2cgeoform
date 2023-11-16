from functools import partial
from typing import TypeVar

import colander
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import subqueryload

from c2cgeoform import JSONDict
from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget
from c2cgeoform.schema import GeoFormManyToManySchemaNode, GeoFormSchemaNode, manytomany_validator
from c2cgeoform.views.abstract_views import AbstractViews, ItemAction, ListField, UserMessage

from ..i18n import _
from ..models.c2cgeoform_demo import Excavation, Situation

_list_field = partial(ListField, Excavation)

base_schema = GeoFormSchemaNode(Excavation)
base_schema.add_before(
    "contact_persons",
    colander.SequenceSchema(
        GeoFormManyToManySchemaNode(Situation),
        name="situations",
        title="Situations",
        widget=RelationCheckBoxListWidget(Situation, "id", "name", order_by="name"),
        validator=manytomany_validator,
    ),
)
base_schema.add_unique_validator(Excavation.reference_number, Excavation.hash)


T = TypeVar("T")


@view_defaults(match_param="table=excavations")
class ExcavationViews(AbstractViews[T]):
    _model = Excavation
    _base_schema = base_schema
    _id_field = "hash"
    _geometry_field = "work_footprint"

    _list_fields = [
        _list_field("reference_number"),
        _list_field("request_date"),
        _list_field("description"),
        _list_field("location_town"),
        _list_field("responsible_company"),
        _list_field(
            "situations",
            renderer=lambda excavation: ", ".join([s.name for s in excavation.situations]),
            filter_column=Situation.name,
        ),
    ]

    MSG_COL = {**AbstractViews.MSG_COL, "error": UserMessage(_("This is an error"), "alert-danger")}

    def _base_query(self) -> JSONDict:
        return super()._base_query().distinct().outerjoin("situations").options(subqueryload("situations"))

    @view_config(route_name="c2cgeoform_index", renderer="../templates/index.jinja2")  # type: ignore[misc]
    def index(self) -> JSONDict:
        return super().index()

    @view_config(route_name="c2cgeoform_grid", renderer="json")  # type: ignore[misc]
    def grid(self) -> JSONDict:
        return super().grid()

    def _grid_actions(self) -> JSONDict:
        return super()._grid_actions() + [
            ItemAction(
                name="action_map",
                label=_("Map"),
                css_class="btn btn-primary btn-map",
                url=self._request.route_url("c2cgeoform_map"),
            )
        ]

    def _item_actions(self, item: str, readonly: bool = False) -> JSONDict:
        actions = super()._item_actions(item, readonly)
        if item is not None:
            actions.append(
                ItemAction(
                    name="error",
                    label=_("Show an error"),
                    icon="glyphicon glyphicon-alert",
                    url=self._request.route_url(
                        self._request.matched_route.name,
                        **self._request.matchdict,
                        _query=[("msg_col", "error")],
                    ),
                )
            )
        return actions

    @view_config(route_name="c2cgeoform_map", renderer="../templates/map.jinja2")  # type: ignore[misc]
    def map(self) -> JSONDict:
        return super().map({})

    @view_config(route_name="c2cgeoform_geojson", renderer="json")  # type: ignore[misc]
    def geojson(self) -> JSONDict:
        return super().geojson()  # type: ignore[no-any-return]

    @view_config(route_name="c2cgeoform_item", request_method="GET", renderer="../templates/edit.jinja2")  # type: ignore[misc]
    def edit(self) -> JSONDict:
        return super().edit()

    @view_config(
        route_name="c2cgeoform_item_duplicate", request_method="GET", renderer="../templates/edit.jinja2"
    )  # type: ignore[misc]
    def duplicate(self) -> JSONDict:
        return super().duplicate()

    @view_config(route_name="c2cgeoform_item", request_method="DELETE", renderer="json")  # type: ignore[misc]
    def delete(self) -> JSONDict:
        return super().delete()

    @view_config(route_name="c2cgeoform_item", request_method="POST", renderer="../templates/edit.jinja2")  # type: ignore[misc]
    def save(self) -> JSONDict:
        return super().save()
