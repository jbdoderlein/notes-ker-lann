# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from api.viewsets import ReadProtectedModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .serializers import ActivitySerializer, ActivityTypeSerializer, EntrySerializer, GuestSerializer
from ..models import Activity, ActivityType, Entry, Guest


class ActivityTypeViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `ActivityType` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/type/
    """
    queryset = ActivityType.objects.order_by('id')
    serializer_class = ActivityTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'manage_entries', 'can_invite', 'guest_entry_fee', ]


class ActivityViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Activity` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/activity/
    """
    queryset = Activity.objects.order_by('id')
    serializer_class = ActivitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'description', 'activity_type', 'location', 'creater', 'organizer', 'attendees_club',
                        'date_start', 'date_end', 'valid', 'open', ]
    search_fields = ['$name', '$description', '$location', '$creater__last_name', '$creater__first_name',
                     '$creater__email', '$creater__note__alias__name', '$creater__note__alias__normalized_name',
                     '$organizer__name', '$organizer__email', '$organizer__note__alias__name',
                     '$organizer__note__alias__normalized_name', '$attendees_club__name', '$attendees_club__email',
                     '$attendees_club__note__alias__name', '$attendees_club__note__alias__normalized_name', ]


class GuestViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Guest` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/guest/
    """
    queryset = Guest.objects.order_by('id')
    serializer_class = GuestSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['activity', 'activity__name', 'last_name', 'first_name', 'inviter', 'inviter__alias__name',
                        'inviter__alias__normalized_name', ]
    search_fields = ['$activity__name', '$last_name', '$first_name', '$inviter__user__email', '$inviter__alias__name',
                     '$inviter__alias__normalized_name', ]


class EntryViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Entry` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/entry/
    """
    queryset = Entry.objects.order_by('id')
    serializer_class = EntrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['activity', 'time', 'note', 'guest', ]
    search_fields = ['$activity__name', '$note__user__email', '$note__alias__name', '$note__alias__normalized_name',
                     '$guest__last_name', '$guest__first_name', ]
