from sqlalchemy.orm import (class_mapper, ColumnProperty, RelationshipProperty)
from sqlalchemy import inspect
from colanderalchemy import SQLAlchemySchemaNode
from . import default_search_paths


class GeoFormSchema():

    _COLANDERALCHEMY = 'colanderalchemy'
    # key to indicate that a field should be shown in the admin list
    _ADMIN_LIST = 'admin_list'

    def __init__(
            self, name, model,
            templates_user=None, templates_admin=None,
            overrides_user=None, overrides_admin=None,
            includes_user=None, includes_admin=None,
            excludes_user=None, excludes_admin=None,
            hash_column_name='hash', show_confirmation=True,
            show_captcha=False, recaptcha_public_key=None,
            recaptcha_private_key=None, **kw):
        self.name = name
        self.model = model
        self.hash_column_name = hash_column_name
        self.show_confirmation = show_confirmation
        self.show_captcha = show_captcha

        if includes_user is not None:
            excludes_user = None
        else:
            excludes_user = [] if excludes_user is None else excludes_user
            excludes_user = excludes_user + [hash_column_name]

        self.schema_user = SQLAlchemySchemaNode(
            self.model,
            overrides=overrides_user,
            includes=includes_user,
            excludes=excludes_user,
            **kw)
        self.schema_admin = SQLAlchemySchemaNode(
            self.model,
            overrides=overrides_admin,
            includes=includes_admin,
            excludes=excludes_admin,
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
                'Model ' + name + ' must have exactly ' +
                'one primary key column')
        self.id_field = meta_model.primary_key[0].name

        if not self._has_hash_column():
            raise RuntimeError(
                'Model ' + name + ' does not contain a ' +
                'hash-value column: ' + hash_column_name)

        self.list_fields = self._get_fields_with_property(self._ADMIN_LIST)

        if show_captcha and (
                recaptcha_public_key is None or
                recaptcha_private_key is None):
            raise RuntimeError(
                '`recaptcha_public_key` and `recaptcha_private_key` must be ' +
                'set when using a captcha')
        self.recaptcha_public_key = recaptcha_public_key
        self.recaptcha_private_key = recaptcha_private_key

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

    def _has_hash_column(self):
        """ Checks if the model contains the hash column.
        """
        mapper = inspect(self.model)
        for column in mapper.attrs:
            if isinstance(column, ColumnProperty):
                if column.columns[0].name == self.hash_column_name:
                    return True
        return False


forms = {}


def register_schema(
        name, model,
        templates_user=None, templates_admin=None,
        overrides_user=None, overrides_admin=None,
        includes_user=None, includes_admin=None,
        excludes_user=None, excludes_admin=None,
        hash_column_name='hash', show_confirmation=True, show_captcha=False,
        recaptcha_public_key=None, recaptcha_private_key=None):
    schema = GeoFormSchema(
        name, model, templates_user, templates_admin,
        overrides_user, overrides_admin, includes_user, includes_admin,
        excludes_user, excludes_admin, hash_column_name, show_confirmation,
        show_captcha, recaptcha_public_key, recaptcha_private_key)
    forms[name] = schema
