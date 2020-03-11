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
    Store current user and IP address in the local thread.
    """
    setattr(_thread_locals, USER_ATTR_NAME, user)
    setattr(_thread_locals, IP_ATTR_NAME, ip)


def get_current_user():
    """
    :return: The user that performed a request (may be anonymous)
    """
    return getattr(_thread_locals, USER_ATTR_NAME, None)


def get_current_ip():
    """
    :return: The IP address of the user that has performed a request
    """
    return getattr(_thread_locals, IP_ATTR_NAME, None)


def get_current_authenticated_user():
    """
    :return: The user that performed a request (must be authenticated, return None if anonymous)
    """
    current_user = get_current_user()
    if isinstance(current_user, AnonymousUser):
        return None
    return current_user


class LogsMiddleware(object):
    """
    This middleware gets the current user with his or her IP address on each request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        This function is called on each request.
        :param request: The HTTP Request
        :return: The HTTP Response
        """
        user = request.user
        # Get request IP from the headers
        # The `REMOTE_ADDR` field may not contain the true IP, if there is a proxy
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
        else:
            ip = request.META.get('REMOTE_ADDR')

        # The user and the IP address are stored in the current thread
        _set_current_user_and_ip(user, ip)
        # The request is then analysed, and the response is generated
        response = self.get_response(request)
        # We flush the connected user and the IP address for the next requests
        _set_current_user_and_ip(None, None)

        return response
