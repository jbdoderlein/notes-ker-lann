# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from member.backends import PermissionBackend
from rest_framework import viewsets

from note_kfet.middlewares import get_current_authenticated_user


class ReadProtectedModelViewSet(viewsets.ModelViewSet):
    """
    Protect a ModelViewSet by filtering the objects that the user cannot see.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = ContentType.objects.get_for_model(self.serializer_class.Meta.model).model_class()
        user = get_current_authenticated_user()
        self.queryset = model.objects.filter(PermissionBackend.filter_queryset(user, model, "view"))


class ReadOnlyProtectedModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Protect a ReadOnlyModelViewSet by filtering the objects that the user cannot see.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = ContentType.objects.get_for_model(self.serializer_class.Meta.model).model_class()
        user = get_current_authenticated_user()
        self.queryset = model.objects.filter(PermissionBackend.filter_queryset(user, model, "view"))
