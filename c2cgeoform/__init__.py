from pkg_resources import resource_filename
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from pyramid.config import Configurator
from deform import Form, widget
from translationstring import TranslationStringFactory


_ = TranslationStringFactory('c2cgeoform')


""" Default search paths for the form templates.
"""
default_search_paths = (
    resource_filename('c2cgeoform', 'templates/widgets'),
    resource_filename('deform', 'templates'))


default_map_settings = {
    'srid': 3857,
    'baseLayers': [{'type_': "OSM"}],
    'view': {
        'projection': 'EPSG:3857',
        'center': [829170, 5933942],
        'zoom': 7,
    },
    'fitSource': False,
    'fitMaxZoom': 14,
    'focusOnly': False,
    'geolocationTooltip': _('Zoom to current location'),
    'zoomInTipLabel': _('Zoom in'),
    'zoomOutTipLabel': _('Zoom out'),
    'mobile': None
}


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
    config.include('.routes')
    config.include('.views')
    config.add_static_view('c2cgeoform_static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')
    config.add_translation_dirs('colander:locale', 'deform:locale', 'locale')

    init_deform(config.root_package.__name__)

    config.scan('c2cgeoform.views')


def translator(term):
    request = get_current_request()
    if request is None:
        return term
    else:
        return get_localizer(request).translate(term)


def init_deform(root_package):
    Form.set_zpt_renderer(default_search_paths, translator=translator)

    node_modules_root = '{}:node_modules'.format(root_package)

    registry = widget.default_resource_registry
    registry.set_js_resources(
        'typeahead', '0.10.5',
        '{}/typeahead.js/dist/typeahead.bundle.min.js'.
        format(node_modules_root))
    registry.set_css_resources(
        'typeahead', '0.10.5',
        'c2cgeoform:static/js/typeaheadjs.css')

    widget.MappingWidget.fields_template = 'mapping_fields'
    widget.FormWidget.fields_template = 'mapping_fields'
