import logging
from deform import Form, ValidationFailure  # , ZPTRendererFactory
from deform.form import Button
from geoalchemy2.elements import WKBElement
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from sqlalchemy import desc, or_, types
from sqlalchemy.exc import DBAPIError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from translationstring import TranslationStringFactory
_ = TranslationStringFactory('c2cgeoform')

logger = logging.getLogger(__name__)

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


def model_attr_info(attr, *keys, default=None):
    if attr is None:
        return default
    value = attr.info
    for key in keys:
        if key not in value:
            return default
        value = value[key]
    return value


class ListField():
    def __init__(self,
                 model=None,
                 attr=None,
                 key=None,
                 label=None,
                 renderer=None,
                 sort_column=None,
                 filter_column=None):
        self._attr = getattr(model, attr) if model else attr
        self._key = key or self._attr.key
        self._label = (label or
                       model_attr_info(self._attr,
                                       'colanderalchemy',
                                       'title') or
                       self._key)
        self._renderer = renderer or self._prop_renderer
        is_column = isinstance(self._attr.property, ColumnProperty)
        self._sort_column = sort_column or (self._attr if is_column else None)
        self._filter_column = filter_column if filter_column is not None \
            else self._attr if is_column \
            else None

    def _prop_renderer(self, entity):
        value = None
        if self._attr is not None:
            value = getattr(entity, self._attr.key)
        if value is None:
            value = ''
        else:
            if isinstance(value, WKBElement):
                value = 'Geometry'
            else:
                value = str(value)
        return value

    def id(self):
        return self._key

    def label(self):
        return self._label

    def value(self, entity):
        return self._renderer(entity)

    def sortable(self):
        return self._sort_column is not None

    def filtrable(self):
        return self._filter_column is not None and \
         isinstance(self._filter_column.type, types.String)

    def sort_column(self):
        return self._sort_column

    def filter_expression(self, term):
        return self._filter_column.ilike(term)


class AbstractViews():

    _model = None  # sqlalchemy model
    _list_fields = []  # Fields in list
    _id_field = None  # Primary key
    _base_schema = None  # base colander schema

    def __init__(self, request):
        self._request = request

    def index(self):
        return {
            'list_fields': self._list_fields
        }

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
        except DBAPIError as e:
            logger.error(str(e), exc_info=True)
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
                if field.filtrable():
                    filters.append(field.filter_expression(search_expr))

            # then join the filters into one `or` condition
            if len(filters) > 0:
                query = query.filter(or_(*filters))

        return query

    def _sort_query(self, query, sort_columns):
        sorts = []
        for col_name, sort_order in sort_columns:
            for field in self._list_fields:
                if field.id() == col_name:
                    sort = field.sort_column()
                    if sort_order == 'desc':
                        sort = desc(sort)
                    sorts.append(sort)
        # Sort on primary key as subqueryload with limit need deterministic
        # order
        for pkey_column in inspect(self._model).primary_key:
            sorts.append(pkey_column)
        query = query.order_by(*sorts)
        return query

    def _grid_rows(self, query, current_page, row_count):
        entities = query
        if row_count != -1:
            entities = entities.limit(row_count) \
                .offset((current_page - 1) * row_count)
        return [
            {f.id(): f.value(entity)
             for f in (
                 self._list_fields +
                 [ListField(self._model, self._id_field, key='_id_')])}
            for entity in entities]

    def _form(self, **kwargs):
        schema = self._base_schema.bind(
            request=self._request,
            dbsession=self._request.dbsession)

        buttons = [Button(name='formsubmit', title=_('Submit'))]

        form = Form(
            schema,
            buttons=buttons,
            **kwargs
            )
        return form

    def _populate_widgets(self, node):
        """ Populate ``deform_ext.RelationSelectMixin`` widgets.
        """
        if hasattr(node.widget, 'populate'):
            node.widget.populate(self._request.dbsession, self._request)

        for child in node:
            self._populate_widgets(child)

    def _get_object(self):
        pk = self._request.matchdict.get('id')
        if pk == "new":
            return self._model()
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

        config = getattr(inspect(self._model).class_, '__c2cgeoform_config__', {})
        duplicable = config.get('duplicate', False)
        new = self._request.matchdict.get('id') == 'new'
        if duplicable and not new:
            duplicable_url = self._request.route_url(
                'c2cgeoform_item_action',
                id=self._request.matchdict.get('id'),
                action='duplicate')
        else:
            duplicable_url = None

        return {
            'form': rendered,
            'deform_dependencies': form.get_widget_resources(),
            'duplicate_url': duplicable_url
        }

    def copy_members_if_duplicates(self, source):
        dest = source.__class__()
        insp = inspect(source.__class__)

        for prop in insp.attrs:
            if isinstance(prop, ColumnProperty):
                is_primary_key = prop.columns[0].primary_key
                to_duplicate = model_attr_info(prop.columns[0],
                                               'c2cgeoform',
                                               'duplicate',
                                               default=True)
                if not is_primary_key and to_duplicate:
                    setattr(dest, prop.key, getattr(source, prop.key))
            if isinstance(prop, RelationshipProperty):
                if model_attr_info(prop,
                                   'c2cgeoform',
                                   'duplicate',
                                   default=True):
                    if prop.cascade.delete:
                        if not prop.uselist:
                            duplicate = self.copy_members_if_duplicates(
                                                getattr(source, prop.key))
                        else:
                            duplicate = [self.copy_members_if_duplicates(m)
                                         for m in getattr(source, prop.key)]
                    else:
                        duplicate = getattr(source, prop.key)
                    setattr(dest, prop.key, duplicate)
        return dest

    def duplicate(self):
        src = self._get_object()
        form = self._form(
            action=self._request.route_url('c2cgeoform_item', id='new'))

        with self._request.dbsession.no_autoflush:
            dest = self.copy_members_if_duplicates(src)
            dict_ = form.schema.dictify(dest)
            self._request.dbsession.expunge_all()

        self._populate_widgets(form.schema)
        rendered = form.render(dict_, request=self._request)

        return {
            'form': rendered,
            'deform_dependencies': form.get_widget_resources()
        }

    def save(self):
        obj = self._get_object()
        try:
            form = self._form()
            form_data = self._request.POST.items()
            obj_dict = form.validate(form_data)
            with self._request.dbsession.no_autoflush:
                obj = form.schema.objectify(obj_dict, obj)
            obj = self._request.dbsession.merge(obj)
            self._request.dbsession.flush()
            return HTTPFound(
                self._request.route_url(
                    'c2cgeoform_item',
                    action='edit',
                    id=obj.__getattribute__(self._id_field)))
        except ValidationFailure as e:
            # FIXME see https://github.com/Pylons/deform/pull/243
            self._populate_widgets(form.schema)
            rendered = e.field.widget.serialize(
                e.field,
                e.cstruct,
                request=self._request)
            return {
                'form': rendered,
                'deform_dependencies': form.get_widget_resources()
            }

    def delete(self):
        obj = self._get_object()
        self._request.dbsession.delete(obj)
        self._request.dbsession.flush()
        return Response('OK')
