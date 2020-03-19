# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from member.backends import PermissionBackend
from rest_framework import viewsets


class ReadProtectedModelViewSet(viewsets.ModelViewSet):
    """
    Protect a ModelViewSet by filtering the objects that the user cannot see.
    """

    def get_queryset(self):
        model = ContentType.objects.get_for_model(self.serializer_class.Meta.model)
        return super().get_queryset().filter(PermissionBackend.filter_queryset(self.request.user, model, "view"))


class ReadOnlyProtectedModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Protect a ReadOnlyModelViewSet by filtering the objects that the user cannot see.
    """

    def get_queryset(self):
        model = ContentType.objects.get_for_model(self.serializer_class.Meta.model)
        return super().get_queryset().filter(PermissionBackend.filter_queryset(self.request.user, model, "view"))
