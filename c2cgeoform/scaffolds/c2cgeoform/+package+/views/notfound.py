import pyramid.request
from c2cgeofom import JSONDict
from pyramid.view import notfound_view_config


@notfound_view_config(renderer="../templates/404.jinja2")  # type: ignore[misc]
def notfound_view(request: pyramid.request.Request) -> JSONDict:
    request.response.status = 404
    return {}
