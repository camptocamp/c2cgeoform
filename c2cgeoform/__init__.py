from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pkg_resources import resource_filename
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

from .models import (DBSession, Base,)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')

    config.add_route('locale', '/locale/')
    config.add_route('form', '/{schema}/form/')
    config.add_route('list', '/{schema}/')
    config.add_route('edit', '/{schema}/{id}/form')

    config.add_translation_dirs('colander:locale', 'deform:locale', 'locale')

    # this should be in the example project
    config.add_translation_dirs('pully/locale')

    config.scan()

    _set_widget_template_path()

    return config.make_wsgi_app()


""" Default search paths for the form templates.
"""
default_search_paths = (
    resource_filename('deform', 'templates'),
    resource_filename('c2cgeoform', 'templates/widgets'))


def translator(term):
    return get_localizer(get_current_request()).translate(term)


def _set_widget_template_path():
    from deform import (Form, widget)

    Form.set_zpt_renderer(default_search_paths, translator=translator)

    registry = widget.ResourceRegistry()
    registry.set_js_resources(
        'json2', None, 'c2cgeoform:static/js/json2.min.js')
    registry.set_js_resources(
        'openlayers', '3.0.0', 'c2cgeoform:static/js/ol.js')
    registry.set_css_resources(
        'openlayers', '3.0.0', 'c2cgeoform:static/js/ol.css')
    registry.set_js_resources(
        'c2cgeoform.deform_map', None,
        'c2cgeoform:static/deform_map/controls.js')
    registry.set_css_resources(
        'c2cgeoform.deform_map', None,
        'c2cgeoform:static/deform_map/style.css')
    Form.set_default_resource_registry(registry)
