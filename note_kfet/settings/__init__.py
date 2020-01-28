import os

from .base import *

app_stage = os.environ.get('DJANGO_APP_STAGE', 'dev')
if app_stage == 'prod':
    from .production import *
else:
    from .development import *

# env variables set at the of in /env/bin/activate
# don't forget to unset in deactivate !

DATABASES["default"]["PASSWORD"] = os.environ.get('DJANGO_DB_PASSWORD','CHANGE_ME_IN_ENV_SETTINGS');
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','CHANGE_ME_IN_ENV_SETTINGS');


