# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from activity.models import ActivityType, Activity, Guest
from rest_framework import serializers

class ActivityTypeSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Activity types.
    The djangorestframework plugin will analyse the model `ActivityType` and parse all fields in the API.
    """
    class Meta:
        model = ActivityType
        fields = '__all__'


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Activities.
    The djangorestframework plugin will analyse the model `Activity` and parse all fields in the API.
    """
    class Meta:
        model = Activity
        fields = '__all__'


class GuestSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Guests.
    The djangorestframework plugin will analyse the model `Guest` and parse all fields in the API.
    """
    class Meta:
        model = Guest
        fields = '__all__'
