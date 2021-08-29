# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from ..models import Profile, Club, Membership


class ProfileSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Profiles.
    The djangorestframework plugin will analyse the model `Profile` and parse all fields in the API.
    """

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('user', )


class ClubSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Clubs.
    The djangorestframework plugin will analyse the model `Club` and parse all fields in the API.
    """

    class Meta:
        model = Club
        fields = '__all__'


class MembershipSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Memberships.
    The djangorestframework plugin will analyse the model `Memberships` and parse all fields in the API.
    """

    class Meta:
        model = Membership
        fields = '__all__'
