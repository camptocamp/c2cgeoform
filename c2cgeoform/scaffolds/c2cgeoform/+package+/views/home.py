import pyramid.request
import pyramid.response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name="home")  # type: ignore[misc]
def home(request: pyramid.request.Request) -> pyramid.response.Response:
    return HTTPFound(request.route_url("c2cgeoform_index", table="excavations"))
