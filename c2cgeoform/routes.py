import warnings
from pyramid.config.actions import action_method


class Application():
    """
    Class used to register and access applications details.

    Example usage

    .. code-block:: python

        application_name = request.application.name()
    """
    def __init__(self, name, models, url_segment=None):
        self._name = name
        self._models = models
        self._url_segment = url_segment or name

    def name(self):
        return self._name

    def url_segment(self):
        return self._url_segment

    def tables(self):
        tables = []
        for key, mapper in self._models:
            ca_config = getattr(mapper, '__colanderalchemy_config__', {})
            table = {}
            # key stand for url path, sometimes designated as table (in match dict)
            table['key'] = key
            table['title'] = ca_config.get('title', mapper.__tablename__)
            table['plural'] = ca_config.get('plural', mapper.__tablename__)
            tables.append(table)
        return tables


class ApplicationRoutePredicate(object):
    """
    Internal route predicate which checks application segment match a
    registered application.
    """
    def __init__(self, val, config):  # pylint: disable=unused-argument
        self._val = val

    def text(self):
        return 'c2cgeoform_application = %s' % (self._val,)

    phash = text

    def __call__(self, context, request):
        app_segment = context['match'].get('application', 'default')
        for application in request.registry['c2cgeoform_applications']:
            if application.url_segment() == app_segment:
                request._c2cgeoform_application = application
                return True
        return False


def pregenerator(request, elements, kw):
    """
    Route pregenerator that set the current matched route application and table
    segments as defaults for generating urls.
    """
    if 'application' not in kw:
        kw['application'] = request.matchdict.get('application', 'default')
    if 'table' not in kw:
        kw['table'] = request.matchdict.get('table', None)
    return elements, kw


@action_method
def add_c2cgeoform_application(config, name, models, url_segment=None):
    def register_application():
        config.registry['c2cgeoform_applications'].append(
            Application(name, models, url_segment=url_segment)
        )
    config.action(
        ('c2cgeoform_application', name),
        register_application
    )


def get_application(request):
    return getattr(request, '_c2cgeoform_application', None)


def includeme(config):
    config.registry.setdefault('c2cgeoform_applications', [])
    config.add_directive('add_c2cgeoform_application', add_c2cgeoform_application)
    config.add_route_predicate('c2cgeoform_application', ApplicationRoutePredicate)
    config.add_request_method(get_application, 'c2cgeoform_application', reify=True)


def register_route(config, route, pattern):
    config.add_route(route,
                     pattern,
                     pregenerator=pregenerator,
                     c2cgeoform_application='registered_application',
                     )


def register_routes(config, multi_application=True):
    if multi_application:
        base_route = '/{application}/{table}'
        register_route(config, 'c2cgeoform_locale', '/{application}/locale')
    else:
        base_route = '/{table}'
        register_route(config, 'c2cgeoform_locale', '/locale')

    register_route(config, 'c2cgeoform_index', base_route)
    register_route(config, 'c2cgeoform_grid', '{}/grid.json'.format(base_route))
    register_route(config, 'c2cgeoform_map', '{}/map'.format(base_route))
    register_route(config, 'c2cgeoform_geojson', '{}/geojson.json'.format(base_route))
    register_route(config, 'c2cgeoform_item', '{}/{{id}}'.format(base_route))
    register_route(config, 'c2cgeoform_item_duplicate', '{}/{{id}}/duplicate'.format(base_route))


def register_models(config, models, url_segment=None):
    """
    Deprecated, use config.add_c2cgeoform_application instead.
    """
    warnings.warn(
        (
            'The "register_models" method is deprecated. '
            'Use "config.add_c2cgeoform_application" instead.'
        ),
        DeprecationWarning,
        stacklevel=3,
    )
    config.add_c2cgeoform_application('default', models, url_segment=url_segment)
    register_routes(config, False)
