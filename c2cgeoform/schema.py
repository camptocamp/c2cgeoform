from sqlalchemy.orm import (class_mapper, ColumnProperty, RelationshipProperty)
from sqlalchemy import inspect
from colanderalchemy import SQLAlchemySchemaNode


class GeoFormSchema():

    _COLANDERALCHEMY = 'colanderalchemy'
    _ADMIN_ONLY = 'admin_only'

    def __init__(
            self, name, model,
            templates_user=None, templates_admin=None):
        self.name = name
        self.model = model

        excludes_user = self._get_user_excludes()
        self.schema_user = SQLAlchemySchemaNode(
            self.model,
            excludes=excludes_user)
        self.schema_admin = SQLAlchemySchemaNode(self.model)

        self.templates_user = templates_user
        self.templates_admin = templates_admin

        meta_model = class_mapper(model)
        if len(meta_model.primary_key) != 1:
            raise RuntimeError(
                'Model ' + meta_model.name + ' must have exactly ' +
                'one primary key column')
        self.id_field = meta_model.primary_key[0].name

    def _get_user_excludes(self):
        """ Search the columns where 'admin_only' is set to True.
        """
        user_excludes = []
        mapper = inspect(self.model)
        for column in mapper.attrs:
            info = {}
            if isinstance(column, ColumnProperty):
                info = column.columns[0].info
            elif isinstance(column, RelationshipProperty):
                info = column.info

            if self._COLANDERALCHEMY in info and \
                    info[self._COLANDERALCHEMY].get(self._ADMIN_ONLY, False):
                user_excludes.append(column.key)
        return user_excludes


forms = {}


def register_schema(
        name, model,
        templates_user=None, templates_admin=None):
    schema = GeoFormSchema(
        name, model, templates_user, templates_admin)
    forms[name] = schema
