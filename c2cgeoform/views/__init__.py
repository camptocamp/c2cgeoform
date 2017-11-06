from pyramid.httpexceptions import HTTPFound


def set_locale_cookie(request):
    """ View to change the preferred language.
    """
    if request.GET['language']:
        language = request.GET['language']
        request.response.set_cookie('_LOCALE_',
                                    value=language,
                                    max_age=31536000)  # max_age = year
    return HTTPFound(location=request.referer,
                     headers=request.response.headers)
