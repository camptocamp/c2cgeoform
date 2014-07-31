from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.events import subscriber, BeforeRender, NewRequest


@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event.get('request')
    if request:
        # make `_` available in Mako templates, so that you can
        # use e.g. `${_(u"Error")}` in the templates
        event['_'] = request.translate
        event['localizer'] = request.localizer

tsf = TranslationStringFactory('c2cgeoform')


@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(string):
        return localizer.translate(tsf(string))

    request.localizer = localizer
    request.translate = auto_translate
