from sqlalchemy.orm import (class_mapper, ColumnProperty, RelationshipProperty)
from sqlalchemy import inspect
from colanderalchemy import SQLAlchemySchemaNode
from . import default_search_paths


class GeoFormSchema():

    _COLANDERALCHEMY = 'colanderalchemy'
    # key to indicate that a field should only be shown in the admin view
    _ADMIN_ONLY = 'admin_only'
    # key to indicate that a field should be shown in the admin list
    _ADMIN_LIST = 'admin_list'

    def __init__(
            self, name, model,
            templates_user=None, templates_admin=None,
            overrides_user=None, overrides_admin=None,
            hash_column_name='hash', **kw):
        self.name = name
        self.model = model
        self.hash_column_name = hash_column_name

        excludes_user = self._get_fields_with_property(self._ADMIN_ONLY)
        self.schema_user = SQLAlchemySchemaNode(
            self.model,
            excludes=(excludes_user + [hash_column_name]),
            overrides=overrides_user,
            **kw)
        self.schema_admin = SQLAlchemySchemaNode(
            self.model,
            overrides=overrides_admin,
            excludes=[hash_column_name],
            **kw)

        self.templates_user = default_search_paths
        if templates_user is not None:
            self.templates_user = (templates_user,) + self.templates_user

        self.templates_admin = default_search_paths
        if templates_admin is not None:
            self.templates_admin = (templates_admin,) + self.templates_admin

        meta_model = class_mapper(model)
        if len(meta_model.primary_key) != 1:
            raise RuntimeError(
                'Model ' + meta_model.name + ' must have exactly ' +
                'one primary key column')
        self.id_field = meta_model.primary_key[0].name

        self.list_fields = self._get_fields_with_property(self._ADMIN_LIST)

    def _get_fields_with_property(self, property):
        """ Search the columns where the given property is set to True.
        """
        fields = []
        mapper = inspect(self.model)
        for column in mapper.attrs:
            info = {}
            if isinstance(column, ColumnProperty):
                info = column.columns[0].info
            elif isinstance(column, RelationshipProperty):
                info = column.info

            if self._COLANDERALCHEMY in info and \
                    info[self._COLANDERALCHEMY].get(property, False):
                fields.append(column.key)
        return fields


forms = {}


def register_schema(
        name, model,
        templates_user=None, templates_admin=None,
        overrides_user=None, overrides_admin=None):
    schema = GeoFormSchema(
        name, model, templates_user, templates_admin,
        overrides_user, overrides_admin)
    forms[name] = schema
