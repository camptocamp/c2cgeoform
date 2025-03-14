from pkg_resources import resource_filename
from pyramid.config import Configurator

import c2cgeoform
from c2cgeoform.settings import apply_local_settings

search_paths = (
    resource_filename("{{cookiecutter.package}}", "templates/widgets"),
    *c2cgeoform.default_search_paths,
)
c2cgeoform.default_search_paths = search_paths


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    apply_local_settings(settings)

    config = Configurator(
        settings=settings, locale_negotiator="{{cookiecutter.package}}.i18n.locale_negotiator"
    )
    config.include("pyramid_chameleon")
    config.include("pyramid_mako")
    config.include("pyramid_jinja2")

    config.include("c2cgeoform")

    config.include(".models")
    config.include(".routes")

    config.add_translation_dirs("locale")

    config.scan()

    return config.make_wsgi_app()
