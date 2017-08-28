from pkg_resources import resource_filename
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from pyramid.events import BeforeRender, NewRequest
from pyramid.config import Configurator

from .subscribers import add_renderer_globals, add_localizer


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    In our case, this is only used for tests.
    """
    config = Configurator(settings=settings)
    return config.make_wsgi_app()


def add_routes_and_views(config):
    # User routes
    config.add_route('form', '/{schema}/form')
    config.add_view('c2cgeoform.views.form',
                    route_name='form',
                    renderer='c2cgeoform:templates/site/form.pt')

    config.add_route('confirm', '/{schema}/form/confirm')
    config.add_view('c2cgeoform.views.confirmation',
                    route_name='confirm',
                    renderer='c2cgeoform:templates/site/confirmation.pt')

    config.add_route('view_user', '/{schema}/form/{hash}')
    config.add_view('c2cgeoform.views.view_user',
                    route_name='view_user',
                    renderer='c2cgeoform:templates/site/view_user.pt')

    # Admin routes
    config.add_route('list', '/admin/{schema}')
    config.add_view('c2cgeoform.views.list',
                    route_name='list',
                    renderer='c2cgeoform:templates/site/list.pt')

    config.add_route('grid', '/admin/{schema}/grid')
    config.add_view('c2cgeoform.views.grid',
                    route_name='grid', renderer='json',
                    request_method='POST')

    config.add_route('view_admin', '/admin/{schema}/{id}')
    config.add_view('c2cgeoform.views.view_admin',
                    route_name='view_admin',
                    renderer='c2cgeoform:templates/site/view_admin.pt')

    config.add_route('edit', '/admin/{schema}/{id}/edit')
    config.add_view('c2cgeoform.views.edit',
                    route_name='edit',
                    renderer='c2cgeoform:templates/site/edit.pt')


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
    config.add_view('c2cgeoform.views.set_locale_cookie',
                    route_name='locale')
    config.add_translation_dirs('colander:locale', 'deform:locale', 'locale')
    config.add_directive('add_c2cgeoform_views', add_routes_and_views)
    _set_widget_template_path()

    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(add_localizer, NewRequest)


""" Default search paths for the form templates.
"""
default_search_paths = (
    resource_filename('c2cgeoform', 'templates/widgets'),
    resource_filename('deform', 'templates'))


def translator(term):
    request = get_current_request()
    if request is None:
        return term
    else:
        return get_localizer(request).translate(term)


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
    registry.set_js_resources(
        'typeahead', '0.10.5',
        'c2cgeoform:static/js/typeahead.bundle-0.10.5.min.js')
    registry.set_css_resources(
        'typeahead', '0.10.5',
        'c2cgeoform:static/js/typeaheadjs.css')
    registry.set_js_resources(
        'c2cgeoform.deform_search', None,
        'c2cgeoform:static/deform_search/search.js')
    Form.set_default_resource_registry(registry)
