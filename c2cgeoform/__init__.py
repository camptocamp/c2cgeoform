from pkg_resources import resource_filename
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from pyramid.events import BeforeRender, NewRequest
from pyramid.config import Configurator
from deform import Form, widget

from .subscribers import add_renderer_globals, add_localizer


""" Default search paths for the form templates.
"""
default_search_paths = (
    resource_filename('c2cgeoform', 'templates/widgets'),
    resource_filename('deform', 'templates'))


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    In our case, this is only used for tests.
    """
    config = Configurator(settings=settings)
    return config.make_wsgi_app()


def includeme(config):
    """
    Function called when "c2cgeoform" is included in a project (with
    ``config.include('c2cgeoform')``).

    This function creates routes and views for c2cgeoform pages.
    """
    config.include('pyramid_chameleon')
    config.include('pyramid_beaker')  # use Beaker for session storage
    config.add_static_view('c2cgeoform_static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')
    config.add_route('locale', '/locale/')
    config.add_view('c2cgeoform.views.set_locale_cookie', route_name='locale')
    config.add_translation_dirs('colander:locale', 'deform:locale', 'locale')

    _set_widget_template_path(config.root_package.__name__)

    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(add_localizer, NewRequest)


def translator(term):
    request = get_current_request()
    if request is None:
        return term
    else:
        return get_localizer(request).translate(term)


def _set_widget_template_path(root_package):
    Form.set_zpt_renderer(default_search_paths, translator=translator)

    node_modules_root = '{}:node_modules'.format(root_package)

    registry = widget.ResourceRegistry()
    registry.set_js_resources(
        'openlayers', '3.0.0',
        '{}/openlayers/dist/ol.js'.format(node_modules_root))
    registry.set_css_resources(
        'openlayers', '3.0.0',
        '{}/openlayers/dist/ol.css'.format(node_modules_root))
    registry.set_js_resources(
        'c2cgeoform.deform_map', None,
        'c2cgeoform:static/deform_map/controls.js')
    registry.set_css_resources(
        'c2cgeoform.deform_map', None,
        'c2cgeoform:static/deform_map/style.css')
    registry.set_js_resources(
        'typeahead', '0.10.5',
        '{}/typeahead.js/dist/typeahead.bundle.min.js'.
        format(node_modules_root))
    registry.set_css_resources(
        'typeahead', '0.10.5',
        'c2cgeoform:static/js/typeaheadjs.css')
    registry.set_js_resources(
        'c2cgeoform.deform_search', None,
        'c2cgeoform:static/deform_search/search.js')
    Form.set_default_resource_registry(registry)
