import os

from .base import *

app_stage = os.environ.get('DJANGO_APP_STAGE', 'dev')
if app_stage == 'prod':
    from .production import *
else:
    from .development import *
# Load password for database and SECRET_KEY

try:
    from .secrets import *
except ImportError:
    from .secrets_example.py import * 
    print("Use default secrets!")
