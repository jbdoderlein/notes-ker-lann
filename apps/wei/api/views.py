# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import WEIClubSerializer, BusSerializer, BusTeamSerializer
from ..models import WEIClub, Bus, BusTeam


class WEIClubViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `WEIClub` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/club/
    """
    queryset = WEIClub.objects.all()
    serializer_class = WEIClubSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['$name', ]
    filterset_fields = ['name', 'year', ]


class BusViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Bus` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/bus/
    """
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['$name', ]
    filterset_fields = ['name', 'wei', ]


class BusTeamViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `BusTeam` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/team/
    """
    queryset = BusTeam.objects.all()
    serializer_class = BusTeamSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['$name', ]
    filterset_fields = ['name', 'bus', 'bus__wei', ]
