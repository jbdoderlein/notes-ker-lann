# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from ..models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Permission types.
    The djangorestframework plugin will analyse the model `Permission` and parse all fields in the API.
    """

    class Meta:
        model = Permission
        fields = '__all__'
