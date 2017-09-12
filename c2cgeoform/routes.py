def includeme(config):

    def table_pregenerator(request, elements, kw):
        if 'table' not in kw:
            kw['table'] = request.matchdict['table']
        return elements, kw

    def rec_with_pregenerator(route, pattern):
        config.add_route(route, pattern, pregenerator=table_pregenerator)

    rec_with_pregenerator('c2cgeoform_index', '/{table}/')
    rec_with_pregenerator('c2cgeoform_grid', '/{table}/grid.json')
    rec_with_pregenerator('c2cgeoform_action', '/{table}/{id}/{action}')
