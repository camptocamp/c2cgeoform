from deform import Form, ValidationFailure  # , ZPTRendererFactory
from deform.form import Button
from geoalchemy2.elements import WKBElement
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from sqlalchemy import desc, or_, types
from sqlalchemy.exc import DBAPIError
from translationstring import TranslationStringFactory

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

    def _col_label(self, col_name):
        col_info = self._model.__getattribute__(self._model, col_name).info
        if 'colanderalchemy' not in col_info:
            return col_name
        if 'title' not in col_info['colanderalchemy']:
            return col_name
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
            params = self._request.params
            current_page = int(params.get('current'))
            row_count = int(params.get('rowCount'))
            search_phrase = params.get('searchPhrase', '').strip()
            sort_columns = self._sort_columns()

            query = self._base_query()
            query = self._filter_query(query, search_phrase)
            query = self._sort_query(query, sort_columns)

            return {
                "current": current_page,
                "rowCount": row_count,
                "rows": self._grid_rows(query, current_page, row_count),
                "total": query.count()
            }
        except DBAPIError:
            return Response(db_err_msg, content_type='text/plain', status=500)

    def _sort_columns(self):
        sort_columns = []
        for key, value in self._request.params.items():
            # Bootgrid sends the sort fields as "sort[col_name]: asc"
            if key.startswith('sort'):
                col_name = key.replace('sort[', '').replace(']', '')
                sort_order = 'asc' if value == 'asc' else 'desc'
                sort_columns.append((col_name, sort_order))
        return sort_columns

    def _base_query(self):
        return self._request.dbsession.query(self._model)

    def _filter_query(self, query, search_phrase):
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
                query = query.filter(or_(*filters))

        return query

    def _sort_query(self, query, sort_columns):
        sorts = []
        for col_name, sort_order in sort_columns:
            if hasattr(self._model, col_name):
                sort = getattr(self._model, col_name)
                if sort_order == 'desc':
                    sort = desc(sort)
                sorts.append(sort)
        if len(sorts) > 0:
            query = query.order_by(*sorts)
        return query

    def _grid_rows(self, query, current_page, row_count):
        """Creates plain objects for the given entities containing
        only those properties flagged with `admin_list`.
        """
        rows = []

        for entity in query.limit(row_count). \
                offset((current_page - 1) * row_count):
            row = {}
            for field in self._list_fields:
                value = getattr(entity, field)
                if value is None:
                    value = ''
                else:
                    if isinstance(value, WKBElement):
                        value = 'Geometry'
                    else:
                        value = str(value)
                row[field] = value
            # set the entity id on a special property
            row['_id_'] = str(getattr(entity, self._id_field))
            rows.append(row)

        return rows

    def _form(self):
        form = Form(
            self._base_schema.clone(),
            buttons=(Button(name='formsubmit', title=_('Submit')),),
            # renderer=renderer,
            # action=self._request.route_url('c2cgeoform_action',))
            )
        # _set_form_widget(form, geo_form_schema.schema_user, template)
        return form

    def _populate_widgets(self, node):
        """ Populate ``deform_ext.RelationSelectMixin`` widgets.
        """
        if hasattr(node.widget, 'populate'):
            node.widget.populate(self._request.dbsession, self._request)

        for child in node:
            self._populate_widgets(child)

    def _new_object(self):
        return self._model()

    def _get_object(self):
        pk = self._request.matchdict.get('id')
        if pk == "new":
            return self._new_object()
        obj = self._request.dbsession.query(self._model) \
            .filter("{0}='{1}'".format(self._id_field, pk)).one_or_none()
        if obj is None:
            raise HTTPNotFound()
        return obj

    def edit(self):
        obj = self._get_object()
        form = self._form()
        self._populate_widgets(form.schema)
        rendered = form.render(form.schema.dictify(obj), request=self._request)
        return({
            'form': rendered,
            'deform_dependencies': form.get_widget_resources()})

    def save(self):
        try:
            form = self._form()
            form_data = self._request.POST.items()
            obj_dict = form.validate(form_data)
            obj = form.schema.objectify(obj_dict)
            obj = self._request.dbsession.merge(obj)
            self._request.dbsession.flush()
            return HTTPFound(
                self._request.route_url(
                    'c2cgeoform_action',
                    action='edit',
                    id=obj.__getattribute__(self._id_field)))
        except ValidationFailure as e:
            # FIXME see https://github.com/Pylons/deform/pull/243
            self._populate_widgets(form.schema)
            rendered = e.field.widget.serialize(
                e.field,
                e.cstruct,
                request=self._request)
            return({
                'form': rendered,
                'deform_dependencies': form.get_widget_resources()})

    def delete(self):
        obj = self._get_object()
        self._request.dbsession.delete(obj)
        self._request.dbsession.flush()
        return HTTPFound(self._request.referer)
