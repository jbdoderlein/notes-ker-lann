# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from member.serializers import ProfileViewSet, ClubViewSet, RoleViewSet, MembershipViewSet
from activity.serializers import ActivityTypeViewSet, ActivityViewSet, GuestViewSet
from note.serializers import NoteViewSet, NoteClubViewSet, NoteUserViewSet, NoteSpecialViewSet, \
                            TransactionViewSet, TransactionTemplateViewSet, MembershipTransactionViewSet

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Users.
    The djangorestframework plugin will analyse the model `User` and parse all fields in the API.
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff',)

class UserViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,
    then render it on /api/users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Routers for members app
router.register(r'members/profile', ProfileViewSet)
router.register(r'members/club', ClubViewSet)
router.register(r'members/role', RoleViewSet)
router.register(r'members/membership', MembershipViewSet)

# Routers for activity app
router.register(r'activity/activity', ActivityViewSet)
router.register(r'activity/type', ActivityTypeViewSet)
router.register(r'activity/guest', GuestViewSet)

# Routers for note app
router.register(r'note/note', NoteViewSet)
router.register(r'note/club', NoteClubViewSet)
router.register(r'note/user', NoteUserViewSet)
router.register(r'note/special', NoteSpecialViewSet)

router.register(r'note/transaction/transaction', TransactionViewSet)
router.register(r'note/transaction/template', TransactionTemplateViewSet)
router.register(r'note/transaction/membership', MembershipTransactionViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]