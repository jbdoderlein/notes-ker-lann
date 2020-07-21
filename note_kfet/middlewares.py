# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User

from threading import local

from django.contrib.sessions.backends.db import SessionStore

USER_ATTR_NAME = getattr(settings, 'LOCAL_USER_ATTR_NAME', '_current_user')
SESSION_ATTR_NAME = getattr(settings, 'LOCAL_SESSION_ATTR_NAME', '_current_session')
IP_ATTR_NAME = getattr(settings, 'LOCAL_IP_ATTR_NAME', '_current_ip')

_thread_locals = local()


def _set_current_user_and_ip(user=None, session=None, ip=None):
    setattr(_thread_locals, USER_ATTR_NAME, user)
    setattr(_thread_locals, SESSION_ATTR_NAME, session)
    setattr(_thread_locals, IP_ATTR_NAME, ip)


def get_current_user() -> User:
    return getattr(_thread_locals, USER_ATTR_NAME, None)


def get_current_session() -> SessionStore:
    return getattr(_thread_locals, SESSION_ATTR_NAME, None)


def get_current_ip() -> str:
    return getattr(_thread_locals, IP_ATTR_NAME, None)


def get_current_authenticated_user():
    current_user = get_current_user()
    if isinstance(current_user, AnonymousUser):
        return None
    return current_user


class SessionMiddleware(object):
    """
    This middleware get the current user with his or her IP address on each request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if 'HTTP_X_REAL_IP' in request.META:
            ip = request.META.get('HTTP_X_REAL_IP')
        elif 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META.get('HTTP_X_FORWARDED_FOR').split(', ')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        _set_current_user_and_ip(user, request.session, ip)
        response = self.get_response(request)
        _set_current_user_and_ip(None, None, None)

        return response


class TurbolinksMiddleware(object):
    """
    Send the `Turbolinks-Location` header in response to a visit that was redirected,
    and Turbolinks will replace the browser's topmost history entry.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        is_turbolinks = request.META.get('HTTP_TURBOLINKS_REFERRER')
        is_response_redirect = response.has_header('Location')

        if is_turbolinks:
            if is_response_redirect:
                location = response['Location']
                prev_location = request.session.pop('_turbolinks_redirect_to', None)
                if prev_location is not None:
                    # relative subsequent redirect
                    if location.startswith('.'):
                        location = prev_location.split('?')[0] + location
                request.session['_turbolinks_redirect_to'] = location
            else:
                if request.session.get('_turbolinks_redirect_to'):
                    location = request.session.pop('_turbolinks_redirect_to')
                    response['Turbolinks-Location'] = location
        return response
