# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import local

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User

REQUEST_ATTR_NAME = getattr(settings, 'LOCAL_REQUEST_ATTR_NAME', '_current_request')

_thread_locals = local()


def _set_current_request(request=None):
    setattr(_thread_locals, REQUEST_ATTR_NAME, request)


def get_current_request():
    return getattr(_thread_locals, REQUEST_ATTR_NAME, None)


class SessionMiddleware(object):
    """
    This middleware get the current user with his or her IP address on each request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If we authenticate through a token to connect to the API, then we query the good user
        if 'HTTP_AUTHORIZATION' in request.META and request.path.startswith("/api"):
            token = request.META.get('HTTP_AUTHORIZATION')
            if token.startswith("Token "):
                token = token[6:]
                from rest_framework.authtoken.models import Token
                if Token.objects.filter(key=token).exists():
                    token_obj = Token.objects.get(key=token)
                    user = token_obj.user
                    request.user = user
                    session = request.session
                    session["permission_mask"] = 42
                    session.save()

        _set_current_request(request)
        response = self.get_response(request)
        _set_current_request(None)

        return response


class LoginByIPMiddleware(object):
    """
    Allow some users to be authenticated based on their IP address.
    For example, the "note" account should not be used elsewhere than the Kfet computer,
    and should not have any password.
    The password that is stored in database should be on the form "ipbased$my.public.ip.address".
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        If the user is not authenticated, get the used IP address
        and check if an user is authorized to be automatically logged with this address.
        If it is the case, the logging is performed with the full rights.
        """
        if not request.user.is_authenticated:
            if 'HTTP_X_REAL_IP' in request.META:
                ip = request.META.get('HTTP_X_REAL_IP')
            elif 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META.get('HTTP_X_FORWARDED_FOR').split(', ')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            qs = User.objects.filter(password__iregex=f"ipbased\\$.*\\^{ip}\\$.*")
            if qs.exists():
                login(request, qs.get())
                session = request.session
                session["permission_mask"] = 42
                session.save()

        return self.get_response(request)


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


class ClacksMiddleware(object):
    """
    Add Clacks Overhead header on each response.
    See https://www.gnuterrypratchett.com/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Clacks-Overhead'] = 'GNU Terry Pratchett'
        return response
