# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import viewsets

from ..models import ActivityType, Activity, Guest
from .serializers import ActivityTypeSerializer, ActivitySerializer, GuestSerializer


class ActivityTypeViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `ActivityType` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/type/
    """
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeSerializer


class ActivityViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Activity` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/activity/
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class GuestViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Guest` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/guest/
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
