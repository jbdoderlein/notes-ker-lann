# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import ActivityTypeSerializer, ActivitySerializer, GuestSerializer
from ..models import ActivityType, Activity, Guest


class ActivityTypeViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `ActivityType` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/type/
    """
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'can_invite', ]


class ActivityViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Activity` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/activity/
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'description', 'activity_type', ]


class GuestViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Guest` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/guest/
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$last_name', '$first_name', '$inviter__alias__name', '$inviter__alias__normalized_name', ]
