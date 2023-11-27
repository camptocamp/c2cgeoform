from typing import Any, Union

import pyramid.request
import pyramid.response
import sqlalchemy.orm
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from c2cgeoform import JSONDict, JSONList


@view_config(route_name="c2cgeoform_locale", renderer="json")  # type: ignore[misc]
def set_locale_cookie(request: pyramid.request.Request) -> Union[JSONDict, pyramid.response.Response]:
    """View to change the preferred language."""
    if request.GET["language"]:
        language = request.GET["language"]
        request.response.set_cookie("_LOCALE_", value=language, max_age=31536000)  # max_age = year
    if request.referer is not None:
        return HTTPFound(location=request.referer, headers=request.response.headers)
    return {"success": True}


class ApplicationViewPredicate:
    """
    Predicate which checks request.application.name() match with passed value.

    Example usage

    .. code-block:: python

        @view_defaults(application='admin')
        class AdminViews():
    """

    def __init__(self, application: str, config: Any):
        del config
        self._application = application

    def text(self) -> str:
        return f"application = {self._application}"

    phash = text

    def __call__(self, info: Any, request: pyramid.request.Request) -> bool:
        return request.application.name() == self._application  # type: ignore[no-any-return]


class TableViewPredicate:
    """
    Predicate which checks request.matchdict['table'] match with passed value.

    Example usage

    .. code-block:: python

        @view_defaults(application='admin', table='users')
        class AdminUserViews():
    """

    def __init__(self, table: str, config: Any):
        del config
        self._table = table

    def text(self) -> str:
        return f"table = {self._table}"

    phash = text

    def __call__(self, info: Any, request: pyramid.request.Request) -> bool:
        return info["match"]["table"] == self._table  # type: ignore[no-any-return]


def includeme(config: pyramid.config.Configurator) -> None:
    config.add_view_predicate("application", ApplicationViewPredicate)
    config.add_view_predicate("table", TableViewPredicate)
