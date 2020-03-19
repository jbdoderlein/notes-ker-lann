# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F

from note.models import Note, NoteUser, NoteClub, NoteSpecial
from note_kfet.middlewares import get_current_session
from .models import Membership, RolePermissions, Club
from django.contrib.auth.backends import ModelBackend


class PermissionBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    @staticmethod
    def permissions(user):
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
                    if permission.mask.rank <= get_current_session().get("permission_mask", 0):
                        yield permission

    @staticmethod
    def filter_queryset(user, model, t, field=None):
        """
        Filter a queryset by considering the permissions of a given user.
        :param user: The owner of the permissions that are fetched
        :param model: The concerned model of the queryset
        :param t: The type of modification (view, add, change, delete)
        :param field: The field of the model to test, if concerned
        :return: A query that corresponds to the filter to give to a queryset
        """

        if user.is_superuser and get_current_session().get("permission_mask", 0) >= 42:
            # Superusers have all rights
            return Q()

        if not isinstance(model, ContentType):
            model = ContentType.objects.get_for_model(model)

        # Never satisfied
        query = Q(pk=-1)
        for perm in PermissionBackend.permissions(user):
            if perm.field and field != perm.field:
                continue
            if perm.model != model or perm.type != t:
                continue
            query = query | perm.query
        return query

    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_superuser and get_current_session().get("permission_mask", 0) >= 42:
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
