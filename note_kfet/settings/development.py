# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

########################
# Development Settings #
########################
# For local dev on your machine:
#  - Enabled by default
#  - use sqlite as a db engine , Debug is True.
#  - standalone mail server
#  - and more ...


import os

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
from . import *

if os.getenv("DJANGO_DEV_STORE_METHOD", "sqllite") == "postgresql":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DJANGO_DB_NAME', 'note_db'),
            'USER': os.environ.get('DJANGO_DB_USER', 'note'),
            'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'CHANGE_ME_IN_ENV_SETTINGS'),
            'HOST': os.environ.get('DJANGO_DB_HOST', 'localhost'),
            'PORT': os.environ.get('DJANGO_DB_PORT', ''),  # Use default port
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Break it, fix it!
DEBUG = True

# Mandatory !
ALLOWED_HOSTS = ['*']

# Emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_SSL = False
# EMAIL_HOST = 'smtp.example.org'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = 'change_me'
# EMAIL_HOST_PASSWORD = 'change_me'

SERVER_EMAIL = 'no-reply@' + os.getenv("DOMAIN", "example.com")

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_AGE = 60 * 60 * 3

STATIC_ROOT = ''  # not needed in development settings
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')]
