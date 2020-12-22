# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import WEIClubSerializer, BusSerializer, BusTeamSerializer, WEIRoleSerializer, \
    WEIRegistrationSerializer, WEIMembershipSerializer
from ..models import WEIClub, Bus, BusTeam, WEIRole, WEIRegistration, WEIMembership


class WEIClubViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `WEIClub` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/club/
    """
    queryset = WEIClub.objects.all()
    serializer_class = WEIClubSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'year', 'date_start', 'date_end', 'email', 'note__alias__name',
                        'note__alias__normalized_name', 'parent_club', 'parent_club__name', 'require_memberships',
                        'membership_fee_paid', 'membership_fee_unpaid', 'membership_duration', 'membership_start',
                        'membership_end', ]
    search_fields = ['$name', '$email', '$note__alias__name', '$note__alias__normalized_name', ]


class BusViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Bus` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/bus/
    """
    queryset = Bus.objects
    serializer_class = BusSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'wei', 'description', ]
    search_fields = ['$name', '$wei__name', '$description', ]


class BusTeamViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `BusTeam` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/team/
    """
    queryset = BusTeam.objects
    serializer_class = BusTeamSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'bus', 'color', 'description', 'bus__wei', ]
    search_fields = ['$name', '$bus__name', '$bus__wei__name', '$description', ]


class WEIRoleViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `WEIRole` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/role/
    """
    queryset = WEIRole.objects
    serializer_class = WEIRoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'permissions', 'for_club', 'membership_set__user', ]
    SearchFilter = ['$name', '$for_club__name', ]


class WEIRegistrationViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all WEIRegistration objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/registration/
    """
    queryset = WEIRegistration.objects
    serializer_class = WEIRegistrationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['user', 'user__username', 'user__first_name', 'user__last_name', 'user__email',
                        'user__note__alias__name', 'user__note__alias__normalized_name', 'wei', 'wei__name',
                        'wei__email', 'wei__note__alias__name', 'wei__note__alias__normalized_name', 'wei__year',
                        'soge_credit', 'caution_check', 'birth_date', 'gender', 'clothing_cut', 'clothing_size',
                        'first_year', 'emergency_contact_name', 'emergency_contact_phone', ]
    search_fields = ['$user__username', '$user__first_name', '$user__last_name', '$user__email',
                     '$user__note__alias__name', '$user__note__alias__normalized_name', '$wei__name',
                     '$wei__email', '$wei__note__alias__name', '$wei__note__alias__normalized_name',
                     '$health_issues', '$emergency_contact_name', '$emergency_contact_phone', ]


class WEIMembershipViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `BusTeam` objects, serialize it to JSON with the given serializer,
    then render it on /api/wei/membership/
    """
    queryset = WEIMembership.objects
    serializer_class = WEIMembershipSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['club__name', 'club__email', 'club__note__alias__name', 'club__note__alias__normalized_name',
                        'user__username', 'user__last_name', 'user__first_name', 'user__email',
                        'user__note__alias__name', 'user__note__alias__normalized_name', 'date_start', 'date_end',
                        'fee', 'roles', 'bus', 'bus__name', 'team', 'team__name', 'registration', ]
    ordering_fields = ['id', 'date_start', 'date_end', ]
    search_fields = ['$club__name', '$club__email', '$club__note__alias__name', '$club__note__alias__normalized_name',
                     '$user__username', '$user__last_name', '$user__first_name', '$user__email',
                     '$user__note__alias__name', '$user__note__alias__normalized_name', '$roles__name',
                     '$bus__name', '$team__name', ]
