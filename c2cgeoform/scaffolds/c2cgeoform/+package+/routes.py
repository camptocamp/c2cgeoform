import os


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('node_modules', 'c2cgeoform_demo:node_modules/')
    config.override_asset(to_override='c2cgeoform_demo:node_modules/',
                          override_with=os.path.join(os.path.dirname(__file__),
                                                     '..',
                                                     'node_modules'))
    config.add_route('home', '/')
    config.add_route('bus_stops', '/bus_stops')
    config.add_route('addresses', '/addresses')

    config.include('c2cgeoform.routes')
