# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later


from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
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


class ContentTypeSerializer(ModelSerializer):
    """
    REST API Serializer for Users.
    The djangorestframework plugin will analyse the model `User` and parse all fields in the API.
    """

    class Meta:
        model = ContentType
        fields = '__all__'
