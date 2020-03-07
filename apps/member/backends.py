# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from member.models import Club, Membership, RolePermissions
from django.contrib.auth.backends import ModelBackend


class PermissionBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def permissions(self, user):
        for membership in Membership.objects.filter(user=user).all():
            if not membership.valid() or membership.roles is None:
                continue
            for role_permissions in RolePermissions.objects.filter(role=membership.roles).all():
                for permission in role_permissions.permissions.all():
                    permission = permission.about(user=user, club=membership.club)
                    yield permission

    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_superuser:
            return True

        if obj is None:
            return False
        perm = perm.split('_', 3)
        perm_type = perm[1]
        perm_field = perm[2] if len(perm) == 3 else None
        return any(permission.applies(obj, perm_type, perm_field) for permission in self.permissions(user_obj))

    def has_module_perms(self, user_obj, app_label):
        return False

    def get_all_permissions(self, user_obj, obj=None):
        return list(self.permissions(user_obj))
