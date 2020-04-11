# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework.filters import SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import WEIClubSerializer
from ..models import WEIClub


class WEIClubViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `WEIClub` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/club/
    """
    queryset = WEIClub.objects.all()
    serializer_class = WEIClubSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$name', ]
