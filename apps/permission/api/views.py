# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters.rest_framework import DjangoFilterBackend
from api.viewsets import ReadOnlyProtectedModelViewSet

from .serializers import PermissionSerializer, RoleSerializer
from ..models import Permission, Role


class PermissionViewSet(ReadOnlyProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Permission` objects, serialize it to JSON with the given serializer,
    then render it on /api/permission/permission/
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['model', 'type', ]


class RoleViewSet(ReadOnlyProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `RolePermission` objects, serialize it to JSON with the given serializer
    then render it on /api/permission/roles/
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', ]
