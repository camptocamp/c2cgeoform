from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pkg_resources import resource_filename

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform:static', 'deform:static')

    config.add_route('form', '/{schema}/form')
    config.add_route('list', '/{schema}')
    config.add_route('edit', '/{schema}/{id}')

    config.scan()

    _set_widget_template_path()

    return config.make_wsgi_app()


""" Default search paths for the form templates.
"""
default_search_paths = (
    resource_filename('deform', 'templates'),
    resource_filename('c2cgeoform', 'templates/widgets'))


def _set_widget_template_path():
    from deform import (Form, widget)

    Form.set_zpt_renderer(default_search_paths)

    registry = widget.ResourceRegistry()
    registry.set_js_resources('json2', None, 'static/js/json2.min.js')
    registry.set_js_resources('openlayers', '3.0.0', 'static/js/ol.js')
    registry.set_css_resources('openlayers', '3.0.0', 'static/js/ol.css')
    registry.set_js_resources(
        'c2cgeoform.deform_map', None, 'static/deform_map/controls.js')
    registry.set_css_resources(
        'c2cgeoform.deform_map', None, 'static/deform_map/style.css')
    Form.set_default_resource_registry(registry)
