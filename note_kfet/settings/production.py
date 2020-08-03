# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import os

########################
# Production  Settings #
########################
# For local dev on your machine:
#  - Enabled by setting env variable DJANGO_APP_STAGE = 'prod'
#  - use Postgresql as db engine
#  - Debug should be false.
#  - should have a dedicated mail server
#  - and more ...

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

# Break it, fix it!
DEBUG = False

# Mandatory !
ALLOWED_HOSTS = [os.environ.get('NOTE_URL', 'localhost')]

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'CHANGE_ME_IN_ENV_SETTINGS')

# Emails
EMAIL_BACKEND = 'mailer.backend.DbBackend'  # Mailer place emails in a queue before sending them to avoid spam
MAILER_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL = False
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.example.org')
EMAIL_PORT = os.getenv('EMAIL_PORT', 465)
EMAIL_HOST_USER = os.getenv('EMAIL_USER', None)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', None)

SERVER_EMAIL = os.getenv("NOTE_MAIL", "notekfet@example.com")
DEFAULT_FROM_EMAIL = "NoteKfet2020 <" + SERVER_EMAIL + ">"

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_AGE = 60 * 60 * 3
