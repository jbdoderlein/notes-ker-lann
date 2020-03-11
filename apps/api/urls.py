# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf.urls import url, include
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import routers, serializers, viewsets
from rest_framework.filters import SearchFilter
from activity.api.urls import register_activity_urls
from member.api.urls import register_members_urls
from note.api.urls import register_note_urls
from logs.api.urls import register_logs_urls


class UserSerializer(serializers.ModelSerializer):
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

class ContentTypeSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Users.
    The djangorestframework plugin will analyse the model `User` and parse all fields in the API.
    """

    class Meta:
        model = ContentType
        fields = '__all__'


class UserViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,
    then render it on /api/users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active', ]
    search_fields = ['$username', '$first_name', '$last_name', ]


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,
    then render it on /api/users/
    """
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer


# Routers provide an easy way of automatically determining the URL conf.
# Register each app API router and user viewset
router = routers.DefaultRouter()
router.register('models', ContentTypeViewSet)
router.register('user', UserViewSet)
register_members_urls(router, 'members')
register_activity_urls(router, 'activity')
register_note_urls(router, 'note')
register_logs_urls(router, 'logs')

app_name = 'api'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('^', include(router.urls)),
    url('^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
