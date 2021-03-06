# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from ..models import Activity, ActivityType, Entry, Guest, GuestTransaction


class ActivityTypeSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Activity types.
    The djangorestframework plugin will analyse the model `ActivityType` and parse all fields in the API.
    """

    class Meta:
        model = ActivityType
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Activities.
    The djangorestframework plugin will analyse the model `Activity` and parse all fields in the API.
    """

    class Meta:
        model = Activity
        fields = '__all__'


class GuestSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Guests.
    The djangorestframework plugin will analyse the model `Guest` and parse all fields in the API.
    """

    class Meta:
        model = Guest
        fields = '__all__'


class EntrySerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Entries.
    The djangorestframework plugin will analyse the model `Entry` and parse all fields in the API.
    """

    class Meta:
        model = Entry
        fields = '__all__'


class GuestTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Special transactions.
    The djangorestframework plugin will analyse the model `GuestTransaction` and parse all fields in the API.
    """

    class Meta:
        model = GuestTransaction
        fields = '__all__'
