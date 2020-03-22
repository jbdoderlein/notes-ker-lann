# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework.filters import SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import ProfileSerializer, ClubSerializer, RoleSerializer, MembershipSerializer
from ..models import Profile, Club, Role, Membership


class ProfileViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Profile` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/profile/
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ClubViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Club` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/club/
    """
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$name', ]


class RoleViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Role` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/role/
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$name', ]


class MembershipViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Membership` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/membership/
    """
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
