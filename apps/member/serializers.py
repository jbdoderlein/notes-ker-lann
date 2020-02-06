# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .models import Profile, Club, Role, Membership
from rest_framework import serializers, viewsets

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Profiles.
    The djangorestframework plugin will analyse the model `Profile` and parse all fields in the API.
    """
    class Meta:
        model = Profile
        fields = '__all__'


class ProfileViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Profile` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/profile/
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ClubSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Clubs.
    The djangorestframework plugin will analyse the model `Club` and parse all fields in the API.
    """
    class Meta:
        model = Club
        fields = '__all__'


class ClubViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Club` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/club/
    """
    queryset = Club.objects.all()
    serializer_class = ClubSerializer


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Roles.
    The djangorestframework plugin will analyse the model `Role` and parse all fields in the API.
    """
    class Meta:
        model = Role
        fields = '__all__'


class RoleViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Role` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/role/
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class MembershipSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Memberships.
    The djangorestframework plugin will analyse the model `Memberships` and parse all fields in the API.
    """
    class Meta:
        model = Membership
        fields = '__all__'


class MembershipViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Membership` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/membership/
    """
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

