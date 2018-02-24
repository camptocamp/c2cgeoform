from pyramid.events import BeforeRender


def table_pregenerator(request, elements, kw):
    if 'table' not in kw:
        kw['table'] = request.matchdict['table']
    return elements, kw


def register_models(config, models, prefix=''):

    def rec_with_pregenerator(route, pattern):
        config.add_route(route, pattern, pregenerator=table_pregenerator)

    tables = []
    for key, mapper in models:
        ca_config = getattr(mapper, '__colanderalchemy_config__', {})
        table = {}
        # key stand for url path, sometimes designated as table (in match dict)
        table['key'] = key
        table['title'] = ca_config.get('title', mapper.__tablename__)
        table['plural'] = ca_config.get('plural', mapper.__tablename__)
        tables.append(table)

    table_regex = '|'.join(['({})'.format(table['key']) for table in tables])
    base_route = '{}/{{table:{}}}'.format(prefix, table_regex)

    rec_with_pregenerator('c2cgeoform_index', base_route)
    rec_with_pregenerator('c2cgeoform_grid', '{}/grid.json'.format(base_route))
    rec_with_pregenerator('c2cgeoform_item', '{}/{{id}}'.format(base_route))
    rec_with_pregenerator('c2cgeoform_item_duplicate', '{}/{{id}}/duplicate'.format(base_route))

    def add_global(event):
        event['tables'] = tables

    config.add_subscriber(add_global, iface=BeforeRender)
