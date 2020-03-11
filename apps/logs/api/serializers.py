# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from ..models import Changelog


class ChangelogSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Changelog types.
    The djangorestframework plugin will analyse the model `Changelog` and parse all fields in the API.
    """

    class Meta:
        model = Changelog
        fields = '__all__'
