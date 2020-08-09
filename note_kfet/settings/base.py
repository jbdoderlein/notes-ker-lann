# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'CHANGE_ME_IN_LOCAL_SETTINGS!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', False)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # External apps
    'mailer',
    'phonenumber_field',
    'polymorphic',
    'crispy_forms',
    'django_tables2',

    # Django contrib
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',

    # API
    'rest_framework',
    'rest_framework.authtoken',

    # Note apps
    'api',
    'activity',
    'logs',
    'member',
    'note',
    'permission',
    'registration',
    'scripts',
    'treasury',
    'wei',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'note_kfet.middlewares.TurbolinksMiddleware',
]

ROOT_URLCONF = 'note_kfet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'note_kfet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DJANGO_DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('DJANGO_DB_USER', 'note'),
        'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),
        'PORT': os.getenv('DJANGO_DB_PORT', ''),  # Use default port
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Limit available languages to this subset
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
    ('fr', _('French')),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# Add some custom statics from /note_kfet/static
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'note_kfet/static'),
]

# Collect statics to /static/
# THIS FOLDER SOULD NOT BE IN GIT TREE!!!
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# Add /apps/ directory to Python modules search path
import sys
sys.path.append(os.path.realpath(os.path.join(BASE_DIR, 'apps')))
print(BASE_DIR, sys.path)

# Use /locale/ for locale files
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# Use /note_kfet/fixtures for database fixtures
FIXTURE_DIRS = [os.path.join(BASE_DIR, 'note_kfet/fixtures')]

# NK15 password hasher for retrocompatibility
# On first login the password will be rehashed with PBKDF2PasswordHasher
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'member.hashers.CustomNK15Hasher',
]

# Custom role-based permission system
AUTHENTICATION_BACKENDS = (
    'permission.backends.PermissionBackend',
)

# Use /media/ for user uploaded media (user profile pictures)
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        # Control API access with our role-based permission system
        'permission.permissions.StrongDjangoObjectPermissions',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Take control on how widget templates are sourced
# See https://docs.djangoproject.com/en/2.2/ref/forms/renderers/#templatessetting
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

# After login redirect user to transfer page
LOGIN_REDIRECT_URL = '/note/transfer/'

# Use Crispy Bootstrap4 theme
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Use Django Table2 Bootstrap4 theme
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap4.html'

# Use only one Django Sites
SITE_ID = 1

# When a server error occured, send an email to these addresses
ADMINS = (
    # ('Admin', 'webmaster@example.com'),
)

# Default regex to validate users aliases
ALIAS_VALIDATOR_REGEX = r''

# Profile picture cropping
PIC_WIDTH = 200
PIC_RATIO = 1

# Custom phone number format
PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'FR'
