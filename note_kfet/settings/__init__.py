import re
from .base import *


def read_env():
    """Pulled from Honcho code with minor updates, reads local default
    environment variables from a .env file located in the project root
    directory.
    """
    try:
        with open('.env') as f:
            content = f.read()
    except IOError:
        content = ''
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))
            os.environ.setdefault(key, val)


read_env()

app_stage = os.environ.get('DJANGO_APP_STAGE', 'dev')
if app_stage == 'prod':
    from .production import *

    DATABASES["default"]["PASSWORD"] = os.environ.get('DJANGO_DB_PASSWORD', 'CHANGE_ME_IN_ENV_SETTINGS')
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'CHANGE_ME_IN_ENV_SETTINGS')
    ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS', 'localhost')]
else:
    from .development import *

try:
    #in secrets.py defines everything you want
    from .secrets import *
except ImportError:
    pass

if "cas" in INSTALLED_APPS:
    MIDDLEWARE += ['cas.middleware.CASMiddleware']
    # CAS Settings
    CAS_AUTO_CREATE_USER = False
    CAS_LOGO_URL = "/static/img/Saperlistpopette.png"
    CAS_FAVICON_URL = "/static/favicon/favicon-32x32.png"
    CAS_SHOW_SERVICE_MESSAGES = True
    CAS_SHOW_POWERED = False
    CAS_REDIRECT_TO_LOGIN_AFTER_LOGOUT = False
    CAS_INFO_MESSAGES = {
        "cas_explained": {
            "message": _(
                u"The Central Authentication Service grants you access to most of our websites by "
                u"authenticating only once, so you don't need to type your credentials again unless "
                u"your session expires or you logout."
            ),
           "discardable": True,
            "type": "info",  # one of info, success, info, warning, danger
       },
    }

    CAS_INFO_MESSAGES_ORDER = [
        'cas_explained',
    ]
    AUTHENTICATION_BACKENDS += ('cas.backends.CASBackend',)
    
if "debug_toolbar" in INSTALLED_APPS:
    MIDDLEWARE.insert(1,"debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = [ '127.0.0.1']
