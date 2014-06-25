from pyramid.view import view_config
from deform import Form, ValidationFailure

from .models import DBSession
from .schema import forms


def _get_schema(request):
    schema_name = request.matchdict['schema']

    if schema_name in forms:
        return forms.get(schema_name)
    else:
        raise RuntimeError('invalid schema \'' + schema_name + '\'')


@view_config(route_name='form', renderer='templates/form.mako')
def form(request):
    geo_form_schema = _get_schema(request)

    form = Form(geo_form_schema.schema_user, buttons=('submit',))

    if 'submit' in request.POST:
        form_data = request.POST.items()

        try:
            obj_dict = form.validate(form_data)
        except ValidationFailure, e:
            return {'form': e.render()}

        obj = geo_form_schema.schema_user.objectify(obj_dict)
        DBSession.add(obj)
        DBSession.flush()

        return {'form': form.render(
            geo_form_schema.schema_user.dictify(obj), readonly=True)}

    return {'form': form.render()}


@view_config(route_name='list', renderer='templates/list.mako')
def list(request):
    geo_form_schema = _get_schema(request)
    entities = DBSession.query(geo_form_schema.model).all()
    return {'entities': entities, 'schema': geo_form_schema}


@view_config(route_name='edit', renderer='templates/edit.mako')
def edit(request):
    geo_form_schema = _get_schema(request)
    form = Form(geo_form_schema.schema_admin, buttons=('submit',))

    if 'submit' in request.POST:
        form_data = request.POST.items()

        try:
            obj_dict = form.validate(form_data)
        except ValidationFailure, e:
            return {'form': e.render(), 'schema': geo_form_schema}

        obj = geo_form_schema.schema_admin.objectify(obj_dict)
        DBSession.merge(obj)
        DBSession.flush()

        return {
            'form': form.render(geo_form_schema.schema_admin.dictify(obj)),
            'schema': geo_form_schema}

    id = request.matchdict['id']
    obj = DBSession.query(geo_form_schema.model).get(id)

    return {
        'form': form.render(geo_form_schema.schema_admin.dictify(obj)),
        'schema': geo_form_schema}
