def includeme(config):

    def table_pregenerator(request, elements, kw):
        if not 'table' in kw:
            kw['table'] = request.matchdict['table']
        return elements, kw

    config.add_route('c2cgeoform_index', '/{table}/', pregenerator=table_pregenerator)
    config.add_route('c2cgeoform_grid', '/{table}/grid.json', pregenerator=table_pregenerator)
    config.add_route('c2cgeoform_new', '/{table}/new', pregenerator=table_pregenerator)
    config.add_route('c2cgeoform_action', '/{table}/{id}/{action}', pregenerator=table_pregenerator)
