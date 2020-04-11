# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from ..models import WEIClub


class WEIClubSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Clubs.
    The djangorestframework plugin will analyse the model `WEIClub` and parse all fields in the API.
    """

    class Meta:
        model = WEIClub
        fields = '__all__'
