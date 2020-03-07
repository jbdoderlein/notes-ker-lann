import os
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
    DATABASES["default"]["PASSWORD"] = os.environ.get('DJANGO_DB_PASSWORD','CHANGE_ME_IN_ENV_SETTINGS')
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','CHANGE_ME_IN_ENV_SETTINGS')
    ALLOWED_HOSTS.append(os.environ.get('ALLOWED_HOSTS','localhost'))
else:
    from .development import *

try:
    from .secrets import *
except ImportError:
    pass

# env variables set at the of in /env/bin/activate
# don't forget to unset in deactivate !

