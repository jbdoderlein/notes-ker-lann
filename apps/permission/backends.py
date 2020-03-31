# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F
from note.models import Note, NoteUser, NoteClub, NoteSpecial
from note_kfet.middlewares import get_current_session
from member.models import Membership, Club

from .models import Permission


class PermissionBackend(ModelBackend):
    """
    Manage permissions of users
    """
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    @staticmethod
    def permissions(user, model, type):
        """
        List all permissions of the given user that applies to a given model and a give type
        :param user: The owner of the permissions
        :param model: The model that the permissions shoud apply
        :param type: The type of the permissions: view, change, add or delete
        :return: A generator of the requested permissions
        """
        for permission in Permission.objects.annotate(club=F("rolepermissions__role__membership__club")) \
                .filter(
            rolepermissions__role__membership__user=user,
            model__app_label=model.app_label,  # For polymorphic models, we don't filter on model type
            type=type,
        ).all():
            if not isinstance(model, permission.model.__class__) or not permission.club:
                continue

            club = Club.objects.get(pk=permission.club)
            permission = permission.about(
                user=user,
                club=club,
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

        if user is None or isinstance(user, AnonymousUser):
            # Anonymous users can't do anything
            return Q(pk=-1)

        if user.is_superuser and get_current_session().get("permission_mask", 0) >= 42:
            # Superusers have all rights
            return Q()

        if not isinstance(model, ContentType):
            model = ContentType.objects.get_for_model(model)

        # Never satisfied
        query = Q(pk=-1)
        perms = PermissionBackend.permissions(user, model, t)
        for perm in perms:
            if perm.field and field != perm.field:
                continue
            if perm.type != t or perm.model != model:
                continue
            perm.update_query()
            query = query | perm.query
        return query

    def has_perm(self, user_obj, perm, obj=None):
        if user_obj is None or isinstance(user_obj, AnonymousUser):
            return False

        if user_obj.is_superuser and get_current_session().get("permission_mask", 0) >= 42:
            return True

        if obj is None:
            return True

        perm = perm.split('.')[-1].split('_', 2)
        perm_type = perm[0]
        perm_field = perm[2] if len(perm) == 3 else None
        ct = ContentType.objects.get_for_model(obj)
        if any(permission.applies(obj, perm_type, perm_field)
               for permission in self.permissions(user_obj, ct, perm_type)):
            return True
        return False

    def has_module_perms(self, user_obj, app_label):
        return False

    def get_all_permissions(self, user_obj, obj=None):
        ct = ContentType.objects.get_for_model(obj)
        return list(self.permissions(user_obj, ct, "view"))
