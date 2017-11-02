import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode


@colander.deferred
def deferred_request(node, kw):
    return kw.get('request')


@colander.deferred
def deferred_dbsession(node, kw):
    return kw.get('dbsession')


@colander.deferred
def deferred_csrf_default(node, kw):
    request = kw.get('request')
    csrf_token = request.session.get_csrf_token()
    return csrf_token


@colander.deferred
def deferred_csrf_validator(node, kw):
    def validate_csrf(node, value):
        request = kw.get('request')
        csrf_token = request.session.get_csrf_token()
        if value != csrf_token:
            raise ValueError('Bad CSRF token')
    return validate_csrf


class GeoFormSchemaNode(SQLAlchemySchemaNode):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.request = deferred_request
        self.dbsession = deferred_dbsession

    def add_csrf_token(self):
        """ Add a csrf_token subnode.
        Validation will be done by pyramid itself using:

        .. code-block:: python

            config.set_default_csrf_options(require_csrf=True)
        """
        self.add(colander.SchemaNode(
            colander.String(),
            name="csrf_token",
            default=deferred_csrf_default,
            widget=deform.widget.HiddenWidget()))
        return self

    def objectify(self, dict_, context=None):
        context = super().objectify(dict_, context)
        return self.dbsession.merge(context)
