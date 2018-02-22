from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.threadlocal import get_current_request
from pyramid.threadlocal import get_current_registry
from pyramid.events import subscriber, BeforeRender, NewRequest


_LOCALE_ = '_LOCALE_'


@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event.get('request')
    if request is None:
        request = get_current_request()
    if request is not None:
        # make `_` available in Chameleon templates, so that you can
        # use e.g. `${_(u"Error")}` in templates
        event['_'] = request.translate
        event['localizer'] = request.localizer


tsf = TranslationStringFactory('c2cgeoform')


@subscriber(NewRequest)
def add_localizer(event):
    _set_accepted_languages_locale(event)
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(string):
        return localizer.translate(tsf(string))

    request.localizer = localizer
    request.translate = auto_translate


def _set_accepted_languages_locale(event):
    """ Set the language depending on the browser settings.
    """
    if getattr(event.request, _LOCALE_, None) is not None or \
       event.request.params.get(_LOCALE_) is not None or \
       event.request.cookies.get(_LOCALE_) is not None:
        # _LOCALE_ was explicitly set, do not change
        return

    # _LOCALE_ is not set, try to get the preferred language
    if not event.request.accept_language:
        return
    accepted = event.request.accept_language

    settings = get_current_registry().settings
    languages = settings['pyramid.available_languages'].split()
    default_language = settings['pyramid.default_locale_name']

    event.request._LOCALE_ = accepted.best_match(languages, default_language)
