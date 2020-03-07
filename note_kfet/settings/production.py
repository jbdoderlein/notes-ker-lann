# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

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
        'NAME': 'note_db',
        'USER': 'note',
        'PASSWORD': 'update_in_env_variable',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

# Break it, fix it!
DEBUG = True

# Mandatory !
ALLOWED_HOSTS = ['127.0.0.1', 'note.comby.xyz']

# Emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_SSL = False
# EMAIL_HOST = 'smtp.example.org'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = 'change_me'
# EMAIL_HOST_PASSWORD = 'change_me'

SERVER_EMAIL = 'no-reply@example.org'

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_AGE = 60 * 60 * 3

# CAS Client settings
CAS_SERVER_URL = "https://note.crans.org/cas/"
