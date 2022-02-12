# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.scopes import BaseScopes
from member.models import Club
from note_kfet.middlewares import get_current_request

from .backends import PermissionBackend
from .models import Permission


class PermissionScopes(BaseScopes):
    """
    An OAuth2 scope is defined by a permission object and a club.
    A token will have a subset of permissions from the owner of the application,
    and can be useful to make queries through the API with limited privileges.
    """

    def get_all_scopes(self):
        return {f"{p.id}_{club.id}": f"{p.description} (club {club.name})"
                for p in Permission.objects.all() for club in Club.objects.all()}

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        if not application:
            return []
        return [f"{p.id}_{p.membership.club.id}"
                for t in Permission.PERMISSION_TYPES
                for p in PermissionBackend.get_raw_permissions(get_current_request(), t[0])]

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        if not application:
            return []
        return [f"{p.id}_{p.membership.club.id}"
                for p in PermissionBackend.get_raw_permissions(get_current_request(), 'view')]


class PermissionOAuth2Validator(OAuth2Validator):
    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """
        User can request as many scope as he wants, including invalid scopes,
        but it will have only the permissions he has.

        This allows clients to request more permission to get finally a
        subset of permissions.
        """

        valid_scopes = set()

        for t in Permission.PERMISSION_TYPES:
            for p in PermissionBackend.get_raw_permissions(get_current_request(), t[0]):
                scope = f"{p.id}_{p.membership.club.id}"
                if scope in scopes:
                    valid_scopes.add(scope)

        request.scopes = valid_scopes

        return valid_scopes
