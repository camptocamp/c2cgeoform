from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name='c2cgeoform_locale', renderer='json')
def set_locale_cookie(request):
    """ View to change the preferred language.
    """
    if request.GET['language']:
        language = request.GET['language']
        request.response.set_cookie('_LOCALE_',
                                    value=language,
                                    max_age=31536000)  # max_age = year
    if request.referer is not None:
        return HTTPFound(location=request.referer,
                         headers=request.response.headers)
    return {"success": True}


class ApplicationViewPredicate(object):
    """
    Predicate which checks request.application.name() match with passed value.

    Example usage

    .. code-block:: python

        @view_defaults(application='admin')
        class AdminViews():
    """
    def __init__(self, application, config):  # pylint: disable=unused-argument
        self._application = application

    def text(self):
        return 'application = %s' % (self._application,)

    phash = text

    def __call__(self, info, request):  # pylint: disable=unused-argument
        return request.application.name() == self._application


class TableViewPredicate(object):
    """
    Predicate which checks request.matchdict['table'] match with passed value.

    Example usage

    .. code-block:: python

        @view_defaults(application='admin', table='users')
        class AdminUserViews():
    """
    def __init__(self, table, config):  # pylint: disable=unused-argument
        self._table = table

    def text(self):
        return 'table = %s' % (self._table,)

    phash = text

    def __call__(self, info, request):  # pylint: disable=unused-argument
        return info['match']['table'] == self._table


def includeme(config):
    config.add_view_predicate('application', ApplicationViewPredicate)
    config.add_view_predicate('table', TableViewPredicate)
