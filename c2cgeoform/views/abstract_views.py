
import paginate

from deform import Form, ValidationFailure  # , ZPTRendererFactory
from deform.form import Button
from geoalchemy2.elements import WKBElement
# from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, or_, types
from translationstring import TranslationStringFactory
from sqlalchemy.exc import DBAPIError
from pyramid.response import Response

import functools

_ = TranslationStringFactory('c2cgeoform')

db_err_msg = """\
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


class AbstractViews():

    _model = None  # sqlalchemy model
    _list_fields = []  # Fields in list
    _id_field = None  # Primary key
    _base_schema = None  # base colander schema

    def __init__(self, request):
        self._request = request

    def _col_label(self, id):
        col_info = self._model.__getattribute__(self._model, id).info
        if 'colanderalchemy' not in col_info:
            return id
        if 'title' not in col_info['colanderalchemy']:
            return id
        to_translate = col_info['colanderalchemy']['title']
        return self._request.localizer.translate(to_translate)

    def index(self):
        list_fields = [(id, self._col_label(id)) for id in self._list_fields]
        return {'list_fields': list_fields}

    def grid(self):
        """API method which serves the JSON data for the Bootgrid table
        in the admin view.
        """
        try:
            current_page = int(self._request.POST.get('current'))
            row_count = int(self._request.POST.get('rowCount'))
            search_phrase = self._request.POST.get('searchPhrase', '').strip()
            sort = self._get_sort_param(self._request.POST)

            query = self._get_query(sort, search_phrase)

            page = paginate.Page(query.all(),
                                 page=current_page,
                                 items_per_page=row_count)

            return {
                "current": page.page,
                "rowCount": page.items_per_page,
                "rows": self._get_grid_rows(page.items),
                "total": page.item_count
            }
        except DBAPIError:
            return Response(db_err_msg, content_type='text/plain', status=500)

    def _get_sort_param(self, params):
        for key in params:
            # Bootgrid sends the sort field as "sort[first_name]: asc"
            if key.startswith('sort'):
                field = key.replace('sort[', '').replace(']', '')
                sort_order = 'asc' if params[key] == 'asc' else 'desc'
                return (field, sort_order)
        return None

    def _get_grid_rows(self, entities):
        """Creates plain objects for the given entities containing
        only those properties flagged with `admin_list`.
        """
        rows = []

        for entity in entities:
            obj = {}
            for field in self._list_fields:
                value = getattr(entity, field)
                if value is None:
                    value = ''
                else:
                    if isinstance(value, WKBElement):
                        value = 'Geometry'
                    else:
                        value = str(value)
                obj[field] = value
            # set the entity id on a special property
            obj['_id_'] = str(getattr(entity, self._id_field))
            rows.append(obj)

        return rows

    def _get_base_query(self):
        return self._request.dbsession.query(self._model)

    def _get_query(self, sort, search_phrase):
        query = self._get_base_query()

        # order by
        if sort is not None and hasattr(self._model, sort[0]):
            sort_field = getattr(self._model, sort[0])
            if sort[1] == 'desc':
                sort_field = desc(sort_field)
            query = query.order_by(sort_field)

        # search
        if search_phrase != '':
            search_expr = '%' + '%'.join(search_phrase.split()) + '%'

            # create `ilike` filters for every list text field
            filters = []
            for field in self._list_fields:
                column = getattr(self._model, field)
                # NOTE only text fields are searched
                if isinstance(column.type, types.String):
                    like = getattr(column, 'ilike')
                    filters.append(like(search_expr))

            # then join the filters into one `or` condition
            if len(filters) > 0:
                filter_expr = filters.pop()
                filter_expr = functools.reduce(
                    lambda filter_expr, filter: or_(filter_expr, filter),
                    filters,
                    filter_expr)
                query = query.filter(filter_expr)

        return query

    def _form(self):
        form = Form(
            self._base_schema.clone(),
            buttons=(Button(name='formsubmit', title=_('Submit')),),
            # renderer=renderer,
            # action=self._request.route_url(self._request.matched_route.name))
            )
        # _set_form_widget(form, geo_form_schema.schema_user, template)
        self._populate_widgets(form.schema)
        return form

    def _populate_widgets(self, schema):
        pass

    def new(self):
        form = self._form()

        if len(self._request.POST) > 0:
            form_data = self._request.POST.items()
            try:
                obj_dict = form.validate(form_data)
                obj = form.schema.objectify(obj_dict)
                self._request.session.add(obj)
                self._request.session.flush()

                # Update server side calculated fields
                # self._request.session.expire(obj)

                return obj

            except ValidationFailure as e:
                # FIXME see https://github.com/Pylons/deform/pull/243
                rendered = e.field.widget.serialize(
                    e.field, e.cstruct, request=self._request)

        else:
            # empty form
            rendered = form.render(form.schema.dictify(self._new_object()),
                                   request=self._request)

        return {
            'form': rendered,
            'deform_dependencies': form.get_widget_resources()}

    def _new_object(self):
        return self._model()

    def _get_object(self):
        pk = self._request.matchdict.get('id')
        return self._get_base_query() \
            .filter("{0}='{1}'".format(self._id_field, pk)).all()[0]

    def view(self):
        raise NotImplementedError()

    def edit(self):
        form = self._form()

        if self._request.method == 'POST':
            form_data = self._request.POST.items()
            try:
                obj_dict = form.validate(form_data)
                obj = form.schema.objectify(obj_dict)
                self._request.dbsession.begin_nested()
                self._request.dbsession.merge(obj)
                self._request.dbsession.commit()

                # Update server side calculated fields
                # self._request.session.expire(obj)

            except ValidationFailure as e:
                # FIXME see https://github.com/Pylons/deform/pull/243
                rendered = e.field.widget.serialize(
                    e.field, e.cstruct, request=self._request)

        obj = self._get_object()
        rendered = form.render(form.schema.dictify(obj), request=self._request)
        return({'form': rendered})

    def delete(self):
        raise NotImplementedError()
