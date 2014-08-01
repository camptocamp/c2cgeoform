from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from deform import Form, ValidationFailure, ZPTRendererFactory

from .models import DBSession
from .schema import forms


def _get_schema(request):
    schema_name = request.matchdict['schema']

    if _is_favicon_request(schema_name):
        # send a 404 for favicon requests that were mapped to the route
        raise HTTPNotFound()
    elif schema_name in forms:
        return forms.get(schema_name)
    else:
        raise HTTPNotFound('invalid schema \'' + schema_name + '\'')


@view_config(route_name='form', renderer='templates/site/form.mako')
def form(request):
    geo_form_schema = _get_schema(request)

    renderer = _get_renderer(geo_form_schema.templates_user)
    form = Form(
        geo_form_schema.schema_user, buttons=('submit',), renderer=renderer)

    if 'submit' in request.POST:
        form_data = request.POST.items()

        try:
            obj_dict = form.validate(form_data)
        except ValidationFailure, e:
            rendered = e.render()
        else:
            obj = geo_form_schema.schema_user.objectify(obj_dict)
            DBSession.add(obj)
            DBSession.flush()

            rendered = form.render(
                geo_form_schema.schema_user.dictify(obj), readonly=True)
    else:
        rendered = form.render()

    return {'form': rendered,
            'deform_dependencies': form.get_widget_resources()}


@view_config(route_name='list', renderer='templates/site/list.mako')
def list(request):
    geo_form_schema = _get_schema(request)
    entities = DBSession.query(geo_form_schema.model).all()
    return {'entities': entities, 'schema': geo_form_schema}


@view_config(route_name='edit', renderer='templates/site/edit.mako')
def edit(request):
    geo_form_schema = _get_schema(request)

    renderer = _get_renderer(geo_form_schema.templates_admin)
    form = Form(
        geo_form_schema.schema_admin, buttons=('submit',), renderer=renderer)

    if 'submit' in request.POST:
        form_data = request.POST.items()

        try:
            obj_dict = form.validate(form_data)
        except ValidationFailure, e:
            rendered = e.render()
        else:
            obj = geo_form_schema.schema_admin.objectify(obj_dict)
            DBSession.merge(obj)
            DBSession.flush()
            rendered = form.render(geo_form_schema.schema_admin.dictify(obj))
    else:
        id = request.matchdict['id']
        obj = DBSession.query(geo_form_schema.model).get(id)
        rendered = form.render(geo_form_schema.schema_admin.dictify(obj))

    return {
        'form': rendered,
        'schema': geo_form_schema,
        'deform_dependencies': form.get_widget_resources()}


@view_config(route_name='locale')
def set_locale_cookie(request):
    """ View to change the preferred language.
    """
    if request.GET['language']:
        language = request.GET['language']
        response = Response()
        response.set_cookie('_LOCALE_',
                            value=language,
                            max_age=31536000)  # max_age = year
    return HTTPFound(location=request.environ['HTTP_REFERER'],
                     headers=response.headers)


def _get_renderer(search_paths):
    if search_paths is None:
        return None
    else:
        from c2cgeoform import translator
        return ZPTRendererFactory(search_paths, translator=translator)


def _is_favicon_request(text):
    return text in [
        'favicon.ico',
        'apple-touch-icon-precomposed.png',
        'apple-touch-icon.png']
