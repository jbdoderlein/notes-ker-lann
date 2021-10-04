# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.defaults import bad_request, permission_denied, page_not_found, server_error
from member.views import CustomLoginView

from .admin import admin_site
from .views import IndexView

urlpatterns = [
    # Dev so redirect to something random
    path('', IndexView.as_view(), name='index'),

    # Include project routers
    path('note/', include('note.urls')),
    path('accounts/', include('member.urls')),
    path('registration/', include('registration.urls')),
    path('activity/', include('activity.urls')),
    path('treasury/', include('treasury.urls')),
    path('wei/', include('wei.urls')),

    # Include Django Contrib and Core routers
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin_site.urls, name="admin"),
    path('accounts/login/', CustomLoginView.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
    path('permission/', include('permission.urls')),

    # Make coffee
    path('coffee/', include('django_htcpcp_tea.urls')),
]

# During development, serve static and media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "oauth2_provider" in settings.INSTALLED_APPS:
    # OAuth2 provider
    urlpatterns.append(
        path('o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
    )

if "cas_server" in settings.INSTALLED_APPS:
    urlpatterns.append(
        path('cas/', include('cas_server.urls', namespace='cas_server'))
    )

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


handler400 = bad_request
handler403 = permission_denied

# Only displayed in production, when debug mode is set to False
handler404 = page_not_found
handler500 = server_error
