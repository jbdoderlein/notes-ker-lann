# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
import re
import os


def read_env():
    """Pulled from Honcho code with minor updates, reads local default
    environment variables from a .env file located in the project root
    directory.
    """
    try:
        with open(os.path.join(BASE_DIR, '.env')) as f:
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


# Try to load environment variables from project .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
read_env()

# Load base settings
from .base import *

# If in dev mode, then override some settings
app_stage = os.getenv('DJANGO_APP_STAGE', 'dev')
if app_stage == 'dev':
    from .development import *

try:
    # in secrets.py defines everything you want
    from .secrets import *

    INSTALLED_APPS += OPTIONAL_APPS

except ImportError:
    pass

if DEBUG:
    PASSWORD_HASHERS += ['member.hashers.DebugSuperuserBackdoor']
    if "debug_toolbar" in INSTALLED_APPS:
        MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = ['127.0.0.1']
