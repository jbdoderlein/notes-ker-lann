# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F

from note.models import Note, NoteUser, NoteClub, NoteSpecial
from .models import Membership, RolePermissions, Club
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
                    permission = permission.about(
                        user=user,
                        club=membership.club,
                        User=User,
                        Club=Club,
                        Membership=Membership,
                        Note=Note,
                        NoteUser=NoteUser,
                        NoteClub=NoteClub,
                        NoteSpecial=NoteSpecial,
                        F=F,
                        Q=Q
                    )
                    yield permission

    def filter_queryset(self, user, model, type, field=None):
        """
        Filter a queryset by considering the permissions of a given user.
        :param user: The owner of the permissions that are fetched
        :param model: The concerned model of the queryset
        :param type: The type of modification (view, add, change, delete)
        :param field: The field of the model to test, if concerned
        :return: A query that corresponds to the filter to give to a queryset
        """

        if user.is_superuser:
            # Superusers have all rights
            return Q()

        # Never satisfied
        query = Q(pk=-1)
        for perm in self.permissions(user):
            if field and field != perm.field:
                continue
            if perm.model != model or perm.type != type:
                continue
            query = query | perm.query
        return query

    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_superuser:
            return True

        if obj is None:
            return True

        perm = perm.split('.')[-1].split('_', 2)
        perm_type = perm[0]
        perm_field = perm[2] if len(perm) == 3 else None
        if any(permission.applies(obj, perm_type, perm_field) for permission in self.permissions(user_obj)):
            return True
        return False

    def has_module_perms(self, user_obj, app_label):
        return False

    def get_all_permissions(self, user_obj, obj=None):
        return list(self.permissions(user_obj))
