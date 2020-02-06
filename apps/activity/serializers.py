# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .models import ActivityType, Activity, Guest
from rest_framework import serializers, viewsets

class ActivityTypeSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Activity types.
    The djangorestframework plugin will analyse the model `ActivityType` and parse all fields in the API.
    """
    class Meta:
        model = ActivityType
        fields = '__all__'


class ActivityTypeViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `ActivityType` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/type/
    """
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeSerializer


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Activities.
    The djangorestframework plugin will analyse the model `Activity` and parse all fields in the API.
    """
    class Meta:
        model = Activity
        fields = '__all__'


class ActivityViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Activity` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/activity/
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class GuestSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Guests.
    The djangorestframework plugin will analyse the model `Guest` and parse all fields in the API.
    """
    class Meta:
        model = Guest
        fields = '__all__'


class GuestViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Guest` objects, serialize it to JSON with the given serializer,
    then render it on /api/activity/guest/
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
