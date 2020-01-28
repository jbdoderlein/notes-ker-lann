import os

from .base import *

app_stage = os.environ.get('DJANGO_APP_STAGE', 'dev')
if app_stage == 'prod':
    from .production import *
else:
    from .development import *
try:
    from .secrets import *
except:
    from .secrets_example.py import * 
