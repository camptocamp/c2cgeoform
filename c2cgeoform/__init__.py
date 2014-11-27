from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pkg_resources import resource_filename
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

from .models import DBSession


def includeme(config):
    """
    Function called when "c2cgeoform" is included in a project (with
    ``config.include('c2cgeoform')``).

    This function creates routes and views for c2cgeoform pages.
    """
    config.include('pyramid_chameleon')
    config.add_static_view('c2cgeoform_static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')
    config.add_route('locale', '/locale/')
    config.add_route('form', '/{schema}/form/')
    config.add_route('list', '/{schema}/')
    config.add_route('grid', '/{schema}/grid/')
    config.add_route('edit', '/{schema}/{id}/form')
    config.add_route('view', '/{schema}/{id}')
    config.add_translation_dirs('colander:locale', 'deform:locale', 'locale')
    config.scan(ignore='c2cgeoform.tests')
    _set_widget_template_path()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.

    This a is test application for the model and templates defined in
    c2cgeoform/pully.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.include(includeme)

    config.add_translation_dirs('pully/locale')

    from .schema import register_schema
    from pully import model
    register_schema(
        'fouille',
        model.ExcavationPermission,
        templates_user=resource_filename('c2cgeoform', 'pully/templates'),
        # override the title for a field in the user form
        overrides_user={'request_date': {'title': 'Date'}})
    model.setup_test_data()

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
