# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F
from django.utils import timezone
from note.models import Note, NoteUser, NoteClub, NoteSpecial
from note_kfet.middlewares import get_current_session
from member.models import Membership, Club

from .decorators import memoize
from .models import Permission


class PermissionBackend(ModelBackend):
    """
    Manage permissions of users
    """
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    @staticmethod
    @memoize
    def get_raw_permissions(user, t):
        """
        Query permissions of a certain type for a user, then memoize it.
        :param user: The owner of the permissions
        :param t: The type of the permissions: view, change, add or delete
        :return: The queryset of the permissions of the user (memoized) grouped by clubs
        """
        if isinstance(user, AnonymousUser):
            # Unauthenticated users have no permissions
            return Permission.objects.none()

        memberships = Membership.objects.filter(user=user).all()
        
        perms = []

        for membership in memberships:
            for role in membership.roles.all():
                for perm in role.permissions.filter(type=t, mask__rank__lte=get_current_session().get("permission_mask", 42)).all():
                    if not perm.permanent:
                        if membership.date_start > timezone.now().date() or membership.date_end < timezone.now().date():
                            continue
                    perm.membership = membership
                    perms.append(perm)
        return perms


    @staticmethod
    def permissions(user, model, type):
        """
        List all permissions of the given user that applies to a given model and a give type
        :param user: The owner of the permissions
        :param model: The model that the permissions shoud apply
        :param type: The type of the permissions: view, change, add or delete
        :return: A generator of the requested permissions
        """

        for permission in PermissionBackend.get_raw_permissions(user, type):
            if not isinstance(model.model_class()(), permission.model.model_class()) or not permission.membership:
                continue

            membership = permission.membership
            club = membership.club

            permission = permission.about(
                user=user,
                club=club,
                membership=membership,
                User=User,
                Club=Club,
                Membership=Membership,
                Note=Note,
                NoteUser=NoteUser,
                NoteClub=NoteClub,
                NoteSpecial=NoteSpecial,
                F=F,
                Q=Q,
                now=timezone.now(),
                today=timezone.now().date(),
            )
            yield permission

    @staticmethod
    @memoize
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

        if user.is_superuser and get_current_session().get("permission_mask", 42) >= 42:
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

    @staticmethod
    @memoize
    def check_perm(user_obj, perm, obj=None):
        """
        Check is the given user has the permission over a given object.
        The result is then memoized.
        Exception: for add permissions, since the object is not hashable since it doesn't have any
        primary key, the result is not memoized. Moreover, the right could change
        (e.g. for a transaction, the balance of the user could change)
        """
        if user_obj is None or isinstance(user_obj, AnonymousUser):
            return False

        sess = get_current_session()
        if sess is not None and sess.session_key is None:
            return False

        if user_obj.is_superuser and get_current_session().get("permission_mask", 42) >= 42:
            return True

        if obj is None:
            return True

        perm = perm.split('.')[-1].split('_', 2)
        perm_type = perm[0]
        perm_field = perm[2] if len(perm) == 3 else None

        ct = ContentType.objects.get_for_model(obj)
        if any(permission.applies(obj, perm_type, perm_field)
               for permission in PermissionBackend.permissions(user_obj, ct, perm_type)):
            return True
        return False

    def has_perm(self, user_obj, perm, obj=None):
        return PermissionBackend.check_perm(user_obj, perm, obj)

    def has_module_perms(self, user_obj, app_label):
        return False

    def get_all_permissions(self, user_obj, obj=None):
        ct = ContentType.objects.get_for_model(obj)
        return list(self.permissions(user_obj, ct, "view"))
