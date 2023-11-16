import warnings
from typing import Any, Optional

import pyramid.config
import pyramid.request
from pyramid.config.actions import action_method

from c2cgeoform import JSONDict


class Application:
    """
    Class used to register and access applications details.

    Example usage

    .. code-block:: python

        application_name = request.application.name()
    """

    def __init__(
        self, name: str, models: list[tuple[str, type[Any]]], url_segment: Optional[str] = None
    ) -> None:
        self._name = name
        self._models = models
        self._url_segment = url_segment or name

    def name(self) -> str:
        return self._name

    def url_segment(self) -> str:
        return self._url_segment

    def tables(self) -> list[JSONDict]:
        tables: list[JSONDict] = []
        for key, mapper in self._models:
            ca_config = getattr(mapper, "__colanderalchemy_config__", {})
            table: JSONDict = {}
            # key stand for url path, sometimes designated as table (in match dict)
            table["key"] = key
            table["title"] = ca_config.get("title", mapper.__tablename__)
            table["plural"] = ca_config.get("plural", mapper.__tablename__)
            tables.append(table)
        return tables


class ApplicationRoutePredicate:
    """
    Internal route predicate which checks application segment match a
    registered application.
    """

    def __init__(self, val: Any, config: pyramid.config.Configurator):
        del config  # unused
        self._val = val

    def text(self) -> str:
        return f"c2cgeoform_application = {self._val}"

    phash = text

    def __call__(self, context: dict[str, Any], request: pyramid.request.Request) -> bool:
        app_segment = context["match"].get("application", "default")
        for application in request.registry["c2cgeoform_applications"]:
            if application.url_segment() == app_segment:
                request._c2cgeoform_application = application
                return True
        return False


def pregenerator(
    request: pyramid.request.Request, elements: list[str], kwargs: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    """
    Route pregenerator that set the current matched route application and table
    segments as defaults for generating urls.
    """
    if "application" not in kwargs:
        kwargs["application"] = request.matchdict.get("application", "default")
    if "table" not in kwargs:
        kwargs["table"] = request.matchdict.get("table", None)
    return elements, kwargs


@action_method  # type: ignore[misc]
def add_c2cgeoform_application(
    config: pyramid.config.Configurator,
    name: str,
    models: list[tuple[str, type[Any]]],
    url_segment: Optional[str] = None,
) -> None:
    def register_application() -> None:
        config.registry["c2cgeoform_applications"].append(Application(name, models, url_segment=url_segment))

    config.action(("c2cgeoform_application", name), register_application)


def get_application(request: pyramid.request.Request) -> Optional[Application]:
    return getattr(request, "_c2cgeoform_application", None)


def includeme(config: pyramid.config.Configurator) -> None:
    config.registry.setdefault("c2cgeoform_applications", [])
    config.add_directive("add_c2cgeoform_application", add_c2cgeoform_application)
    config.add_route_predicate("c2cgeoform_application", ApplicationRoutePredicate)
    config.add_request_method(get_application, "c2cgeoform_application", reify=True)


def register_route(config: pyramid.config.Configurator, route: str, pattern: str) -> None:
    config.add_route(
        route,
        pattern,
        pregenerator=pregenerator,
        c2cgeoform_application="registered_application",
    )


def register_routes(config: pyramid.config.Configurator, multi_application: bool = True) -> None:
    if multi_application:
        base_route = "/{application}/{table}"
        register_route(config, "c2cgeoform_locale", "/{application}/locale")
    else:
        base_route = "/{table}"
        register_route(config, "c2cgeoform_locale", "/locale")

    register_route(config, "c2cgeoform_index", base_route)
    register_route(config, "c2cgeoform_grid", f"{base_route}/grid.json")
    register_route(config, "c2cgeoform_map", f"{base_route}/map")
    register_route(config, "c2cgeoform_geojson", f"{base_route}/geojson.json")
    register_route(config, "c2cgeoform_item", f"{base_route}/{{id}}")
    register_route(config, "c2cgeoform_item_duplicate", f"{base_route}/{{id}}/duplicate")


def register_models(
    config: pyramid.config.Configurator, models: type[Any], url_segment: Optional[str] = None
) -> None:
    """
    Deprecated, use config.add_c2cgeoform_application instead.
    """
    warnings.warn(
        'The "register_models" method is deprecated. Use "config.add_c2cgeoform_application" instead.',
        DeprecationWarning,
        stacklevel=3,
    )
    config.add_c2cgeoform_application("default", models, url_segment=url_segment)
    register_routes(config, False)
