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


class ListField():
    def __init__(self, field, key=None, label=None, renderer=None):
        self.field = field
        self.key = key
        self.label = label
        self.renderer = renderer

    def get_col_id(self):
        if self.key is not None:
            return self.key
        return self.field

    def get_col_label(self, model):
        if self.label is not None:
            return self.label
        col_info = getattr(model, self.field).info
        if 'colanderalchemy' not in col_info:
            return self.field
        if 'title' not in col_info['colanderalchemy']:
            return self.field
        return col_info['colanderalchemy']['title']

    def get_col_value(self, entity):
        if self.renderer is not None:
            return self.renderer(entity)
        value = getattr(entity, self.field)
        if value is None:
            value = ''
        else:
            if isinstance(value, WKBElement):
                value = 'Geometry'
            else:
                value = str(value)
        return value


class AbstractViews():

    _model = None  # sqlalchemy model
    _list_fields = []  # Fields in list
    _id_field = None  # Primary key
    _base_schema = None  # base colander schema

    def __init__(self, request):
        self._request = request

    def index(self):
        list_fields = [(field.get_col_id(), field.get_col_label(self._model))
                       for field in self._list_fields]
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
        entities = query.limit(row_count) \
            .offset((current_page - 1) * row_count)
        fields = self._list_fields + [ListField(self._id_field, key='_id_')]
        return [{f.get_col_id(): f.get_col_value(entity) for f in fields}
                for entity in entities]

    def _form(self):
        schema = self._base_schema.bind(
            request=self._request,
            dbsession=self._request.dbsession)

        form = Form(
            schema,
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
        obj = self._request.dbsession.query(self._model). \
            filter(getattr(self._model, self._id_field) == pk). \
            one_or_none()
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
        obj = self._get_object()
        try:
            form = self._form()
            form_data = self._request.POST.items()
            obj_dict = form.validate(form_data)
            obj = form.schema.objectify(obj_dict, obj)
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
        return Response('OK')
