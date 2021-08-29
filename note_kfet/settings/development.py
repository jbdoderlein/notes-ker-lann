# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

########################
# Development Settings #
########################
# For local dev on your machine:
#  - debug by default
#  - use sqlite as a db engine by default
#  - standalone mail server
#  - and more...

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if os.getenv("DJANGO_DEV_STORE_METHOD", "sqlite") != "postgresql":
    # Use an SQLite database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Dummy cache for development
# https://docs.djangoproject.com/en/2.2/topics/cache/#setting-up-the-cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Break it, fix it!
DEBUG = True

# Allow access from all hostnames
ALLOWED_HOSTS = ['*']

# Drop emails to server console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SERVER_EMAIL = 'notekfet@localhost'

# Disable some security settings
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_AGE = 60 * 60 * 3
