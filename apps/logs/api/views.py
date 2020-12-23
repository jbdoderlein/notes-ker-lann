# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from api.viewsets import ReadOnlyProtectedModelViewSet

from .serializers import ChangelogSerializer
from ..models import Changelog


class ChangelogViewSet(ReadOnlyProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Changelog` objects, serialize it to JSON with the given serializer,
    then render it on /api/logs/
    """
    queryset = Changelog.objects.order_by('id')
    serializer_class = ChangelogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['model', 'action', "instance_pk", 'user', 'ip', ]
    ordering_fields = ['timestamp', 'id', ]
    ordering = ['-id', ]
