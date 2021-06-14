# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from api.viewsets import ReadOnlyProtectedModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .serializers import PermissionSerializer, RoleSerializer
from ..models import Permission, Role


class PermissionViewSet(ReadOnlyProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Permission` objects, serialize it to JSON with the given serializer,
    then render it on /api/permission/permission/
    """
    queryset = Permission.objects.order_by('id')
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['model', 'type', 'query', 'mask', 'field', 'permanent', ]
    search_fields = ['$model__name', '$query', '$description', ]


class RoleViewSet(ReadOnlyProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `RolePermission` objects, serialize it to JSON with the given serializer
    then render it on /api/permission/roles/
    """
    queryset = Role.objects.order_by('id')
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'permissions', 'for_club', 'memberships__user', ]
    search_fields = ['$name', '$for_club__name', ]
