from pyramid.csrf import SessionCSRFStoragePolicy
#from pyramid.session import BaseCookieSessionFactory
from pyramid_nacl_session import EncryptedCookieSessionFactory
from pyramid_nacl_session import generate_secret


def includeme(config):
    settings = config.get_settings()
    if 'session_secret' in settings:
        hex_secret = settings['session_secret'].strip()
        secret = binascii.unhexlify(hex_secret)
    else:
        secret = generate_secret(as_hex=False)
    factory = EncryptedCookieSessionFactory(secret)
    config.set_session_factory(factory)
    config.set_default_csrf_options(require_csrf=True)
    config.set_csrf_storage_policy(SessionCSRFStoragePolicy())
