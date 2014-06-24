from sqlalchemy.orm import class_mapper
from colanderalchemy import SQLAlchemySchemaNode


class GeoFormSchema():
    def __init__(
            self, name, model,
            includes_user=None, excludes_user=None,
            includes_admin=None, excludes_admin=None):
        self.name = name
        self.model = model
        self.schema_user = SQLAlchemySchemaNode(
            self.model,
            includes=includes_user, excludes=excludes_user)
        self.schema_admin = SQLAlchemySchemaNode(
            self.model,
            includes=includes_admin, excludes=excludes_admin)

        meta_model = class_mapper(model)
        if len(meta_model.primary_key) != 1:
            raise RuntimeError(
                'Model ' + meta_model.name + ' must have exactly ' +
                'one primary key column')
        self.id_field = meta_model.primary_key[0].name

forms = {}


def register_schema(
        name, model,
        includes_user=None, excludes_user=None,
        includes_admin=None, excludes_admin=None):
    schema = GeoFormSchema(
        name, model, includes_user, excludes_user,
        includes_admin, excludes_admin)
    forms[name] = schema
