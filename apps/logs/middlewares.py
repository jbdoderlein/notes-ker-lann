# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from threading import local


USER_ATTR_NAME = getattr(settings, 'LOCAL_USER_ATTR_NAME', '_current_user')
IP_ATTR_NAME = getattr(settings, 'LOCAL_IP_ATTR_NAME', '_current_ip')

_thread_locals = local()


def _set_current_user_and_ip(user=None, ip=None):
    """
    Sets current user in local thread.
    Can be used as a hook e.g. for shell jobs (when request object is not
    available).
    """
    setattr(_thread_locals, USER_ATTR_NAME, user)
    setattr(_thread_locals, IP_ATTR_NAME, ip)


def get_current_user():
    return getattr(_thread_locals, USER_ATTR_NAME, None)


def get_current_ip():
    return getattr(_thread_locals, IP_ATTR_NAME, None)


def get_current_authenticated_user():
    current_user = get_current_user()
    if isinstance(current_user, AnonymousUser):
        return None
    return current_user


class LogsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
        else:
            ip = request.META.get('REMOTE_ADDR')

        _set_current_user_and_ip(user, ip)

        response = self.get_response(request)

        return response
