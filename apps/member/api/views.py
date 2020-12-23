# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import ProfileSerializer, ClubSerializer, MembershipSerializer
from ..models import Profile, Club, Membership


class ProfileViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Profile` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/profile/
    """
    queryset = Profile.objects.order_by('id')
    serializer_class = ProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['user', 'user__first_name', 'user__last_name', 'user__username', 'user__email',
                        'user__note__alias__name', 'user__note__alias__normalized_name', 'phone_number', "section",
                        'department', 'promotion', 'address', 'paid', 'ml_events_registration', 'ml_sport_registration',
                        'ml_art_registration', 'report_frequency', 'email_confirmed', 'registration_valid', ]
    search_fields = ['$user__first_name', '$user__last_name', '$user__username', '$user__email',
                     '$user__note__alias__name', '$user__note__alias__normalized_name', ]


class ClubViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Club` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/club/
    """
    queryset = Club.objects.order_by('id')
    serializer_class = ClubSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'email', 'note__alias__name', 'note__alias__normalized_name', 'parent_club',
                        'parent_club__name', 'require_memberships', 'membership_fee_paid', 'membership_fee_unpaid',
                        'membership_duration', 'membership_start', 'membership_end', ]
    search_fields = ['$name', '$email', '$note__alias__name', '$note__alias__normalized_name', ]


class MembershipViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Membership` objects, serialize it to JSON with the given serializer,
    then render it on /api/members/membership/
    """
    queryset = Membership.objects.order_by('id')
    serializer_class = MembershipSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['club__name', 'club__email', 'club__note__alias__name', 'club__note__alias__normalized_name',
                        'user__username', 'user__last_name', 'user__first_name', 'user__email',
                        'user__note__alias__name', 'user__note__alias__normalized_name',
                        'date_start', 'date_end', 'fee', 'roles', ]
    ordering_fields = ['id', 'date_start', 'date_end', ]
    search_fields = ['$club__name', '$club__email', '$club__note__alias__name', '$club__note__alias__normalized_name',
                     '$user__username', '$user__last_name', '$user__first_name', '$user__email',
                     '$user__note__alias__name', '$user__note__alias__normalized_name', '$roles__name', ]
