# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later


from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from member.api.serializers import ProfileSerializer, MembershipSerializer
from note.models import Alias


class UserSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Users.
    The djangorestframework plugin will analyse the model `User` and parse all fields in the API.
    """

    class Meta:
        model = User
        exclude = (
            'password',
            'groups',
            'user_permissions',
        )


class ContentTypeSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Users.
    The djangorestframework plugin will analyse the model `User` and parse all fields in the API.
    """

    class Meta:
        model = ContentType
        fields = '__all__'


class OAuthSerializer(serializers.ModelSerializer):
    """
    Informations that are transmitted by OAuth.
    For now, this includes user, profile and valid memberships.
    This should be better managed later.
    """
    normalized_name = serializers.SerializerMethodField()

    profile = ProfileSerializer()

    memberships = serializers.SerializerMethodField()

    def get_normalized_name(self, obj):
        return Alias.normalize(obj.username)

    def get_memberships(self, obj):
        return serializers.ListSerializer(child=MembershipSerializer()).to_representation(
            obj.memberships.filter(date_start__lte=timezone.now(), date_end__gte=timezone.now()))

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'normalized_name',
            'first_name',
            'last_name',
            'email',
            'is_superuser',
            'is_active',
            'is_staff',
            'profile',
            'memberships',
        )
