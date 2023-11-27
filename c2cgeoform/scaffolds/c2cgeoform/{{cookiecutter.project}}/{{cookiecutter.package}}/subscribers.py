from pyramid.events import BeforeRender, NewRequest, subscriber
from pyramid.i18n import TranslationStringFactory, get_localizer

# see https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/templates/mako_i18n.html*


@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event["request"]
    event["_"] = request.translate
    event["localizer"] = request.localizer


tsf1 = TranslationStringFactory("{{cookiecutter.package}}")
tsf2 = TranslationStringFactory("c2cgeoform")


@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(*args, **kwargs):
        result = localizer.translate(tsf1(*args, **kwargs))
        return localizer.translate(tsf2(*args, **kwargs)) if result == args[0] else result

    request.localizer = localizer
    request.translate = auto_translate
