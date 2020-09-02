# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import routers, serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from api.viewsets import ReadProtectedModelViewSet
from note.models import Alias


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


class UserViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,
    then render it on /api/users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active', ]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Sqlite doesn't support ORDER BY in subqueries
        queryset = queryset.order_by("username") \
            if settings.DATABASES[queryset.db]["ENGINE"] == 'django.db.backends.postgresql' else queryset

        if "search" in self.request.GET:
            pattern = self.request.GET["search"]

            # We match first a user by its username, then if an alias is matched without normalization
            # And finally if the normalized pattern matches a normalized alias.
            queryset = queryset.filter(
                username__iregex="^" + pattern
            ).union(
                queryset.filter(
                    Q(note__alias__name__iregex="^" + pattern)
                    & ~Q(username__iregex="^" + pattern)
                ), all=True).union(
                queryset.filter(
                    Q(note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
                    & ~Q(note__alias__name__iregex="^" + pattern)
                    & ~Q(username__iregex="^" + pattern)
                ),
                all=True).union(
                queryset.filter(
                    Q(note__alias__normalized_name__iregex="^" + pattern.lower())
                    & ~Q(note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
                    & ~Q(note__alias__name__iregex="^" + pattern)
                    & ~Q(username__iregex="^" + pattern)
                ),
                all=True).union(
                queryset.filter(
                    (Q(last_name__iregex="^" + pattern) | Q(first_name__iregex="^" + pattern))
                    & ~Q(note__alias__normalized_name__iregex="^" + pattern.lower())
                    & ~Q(note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
                    & ~Q(note__alias__name__iregex="^" + pattern)
                    & ~Q(username__iregex="^" + pattern)
                ),
                all=True)

        queryset = queryset if settings.DATABASES[queryset.db]["ENGINE"] == 'django.db.backends.postgresql' \
            else queryset.order_by("username")

        return queryset


# This ViewSet is the only one that is accessible from all authenticated users!
class ContentTypeViewSet(ReadOnlyModelViewSet):
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

if "member" in settings.INSTALLED_APPS:
    from member.api.urls import register_members_urls
    register_members_urls(router, 'members')

if "member" in settings.INSTALLED_APPS:
    from activity.api.urls import register_activity_urls
    register_activity_urls(router, 'activity')

if "note" in settings.INSTALLED_APPS:
    from note.api.urls import register_note_urls
    register_note_urls(router, 'note')

if "treasury" in settings.INSTALLED_APPS:
    from treasury.api.urls import register_treasury_urls
    register_treasury_urls(router, 'treasury')

if "permission" in settings.INSTALLED_APPS:
    from permission.api.urls import register_permission_urls
    register_permission_urls(router, 'permission')

if "logs" in settings.INSTALLED_APPS:
    from logs.api.urls import register_logs_urls
    register_logs_urls(router, 'logs')

if "wei" in settings.INSTALLED_APPS:
    from wei.api.urls import register_wei_urls
    register_wei_urls(router, 'wei')

app_name = 'api'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('^', include(router.urls)),
    url('^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
