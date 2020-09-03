# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from permission.backends import PermissionBackend
from note_kfet.middlewares import get_current_session
from note.models import Alias

from .serializers import UserSerializer, ContentTypeSerializer


class ReadProtectedModelViewSet(ModelViewSet):
    """
    Protect a ModelViewSet by filtering the objects that the user cannot see.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = ContentType.objects.get_for_model(self.serializer_class.Meta.model).model_class()

    def get_queryset(self):
        user = self.request.user
        get_current_session().setdefault("permission_mask", 42)
        return self.model.objects.filter(PermissionBackend.filter_queryset(user, self.model, "view")).distinct()


class ReadOnlyProtectedModelViewSet(ReadOnlyModelViewSet):
    """
    Protect a ReadOnlyModelViewSet by filtering the objects that the user cannot see.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = ContentType.objects.get_for_model(self.serializer_class.Meta.model).model_class()

    def get_queryset(self):
        user = self.request.user
        get_current_session().setdefault("permission_mask", 42)
        return self.model.objects.filter(PermissionBackend.filter_queryset(user, self.model, "view")).distinct()


class UserViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,
    then render it on /api/users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active', ]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Sqlite doesn't support ORDER BY in subqueries
        queryset = queryset.order_by("username") \
            if settings.DATABASES[queryset.db]["ENGINE"] == 'django.db.backends.postgresql' else queryset

        if "search" in self.request.GET:
            pattern = self.request.GET["search"]

            # We match first a user by its username, then if an alias is matched without normalization
            # And finally if the normalized pattern matches a normalized alias.
            queryset = queryset.filter(
                           username__iregex="^" + pattern).union(
                       queryset.filter(
                           Q(note__alias__name__iregex="^" + pattern)
                           & ~Q(username__iregex="^" + pattern)), all=True).union(
                       queryset.filter(
                           Q(note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
                           & ~Q(note__alias__name__iregex="^" + pattern)
                           & ~Q(username__iregex="^" + pattern)), all=True).union(
                       queryset.filter(
                           Q(note__alias__normalized_name__iregex="^" + pattern.lower())
                           & ~Q(note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
                           & ~Q(note__alias__name__iregex="^" + pattern)
                           & ~Q(username__iregex="^" + pattern)), all=True).union(
                       queryset.filter(
                           (Q(last_name__iregex="^" + pattern) | Q(first_name__iregex="^" + pattern))
                           & ~Q(note__alias__normalized_name__iregex="^" + pattern.lower())
                           & ~Q(note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
                           & ~Q(note__alias__name__iregex="^" + pattern)
                           & ~Q(username__iregex="^" + pattern)), all=True)

        queryset = queryset if settings.DATABASES[queryset.db]["ENGINE"] == 'django.db.backends.postgresql' \
            else queryset.order_by("username")

        return queryset


# This ViewSet is the only one that is accessible from all authenticated users!
class ContentTypeViewSet(ReadOnlyModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,
    then render it on /api/users/
    """
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
