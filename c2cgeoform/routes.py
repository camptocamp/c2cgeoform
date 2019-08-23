from pyramid.events import BeforeRender


class Application():

    def __init__(self, name, models):
        self._name = name
        self._models = models

    def name(self):
        return self._name

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


applications = {}


def pregenerator(request, elements, kw):
    if 'table' not in kw:
        kw['table'] = request.matchdict['table']
    if 'application' not in kw:
        kw['application'] = request.matchdict['application']
    return elements, kw


def register_application(name, models):
    global applications
    applications[name] = Application(name, models)


def register_routes(config, multi_application=True, prefix=''):
    app_regex = '|'.join(applications.keys())

    if multi_application:
        base_route = '{}/{{application:{}}}/{{table}}'.format(prefix, app_regex)
    else:
        base_route = '{}/{{table}}'.format(prefix)

    def rec_with_pregenerator(route, pattern):
        config.add_route(route, pattern, pregenerator=pregenerator)

    rec_with_pregenerator('c2cgeoform_index', base_route)
    rec_with_pregenerator('c2cgeoform_grid', '{}/grid.json'.format(base_route))
    rec_with_pregenerator('c2cgeoform_item', '{}/{{id}}'.format(base_route))
    rec_with_pregenerator('c2cgeoform_item_duplicate', '{}/{{id}}/duplicate'.format(base_route))

    def add_global(event):
        event['applications'] = applications

    config.add_subscriber(add_global, iface=BeforeRender)


def register_models(config, models, prefix=''):
    """
    Deprecated, use register_application and register_routes instead
    """
    register_application('default', models)
    register_routes(config, False, prefix)
