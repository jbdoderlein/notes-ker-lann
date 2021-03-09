# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers

from .views import UserInformationView
from .viewsets import ContentTypeViewSet, UserViewSet

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
    url('me', UserInformationView.as_view()),
    url('^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
