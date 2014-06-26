from pyramid.config import Configurator
from sqlalchemy import engine_from_config

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
    config.add_static_view('static-deform', 'deform:static')

    config.add_route('form', '/{schema}/form')
    config.add_route('list', '/{schema}')
    config.add_route('edit', '/{schema}/{id}')

    config.scan()

    set_widget_template_path()

    return config.make_wsgi_app()


def set_widget_template_path():
    from pkg_resources import resource_filename
    from deform import Form

    deform_templates = resource_filename('deform', 'templates')
    custom_templates = resource_filename('c2cgeoform', 'templates/widgets')
    search_path = (custom_templates, deform_templates)

    Form.set_zpt_renderer(search_path)
