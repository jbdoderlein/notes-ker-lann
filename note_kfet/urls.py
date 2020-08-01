# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.defaults import bad_request, permission_denied, page_not_found, server_error
from django.views.generic import RedirectView

from member.views import CustomLoginView

from .admin import admin_site

urlpatterns = [
    # Dev so redirect to something random
    path('', RedirectView.as_view(pattern_name='note:transfer'), name='index'),

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
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if "cas_server" in settings.INSTALLED_APPS:
    urlpatterns += [
        # Include CAS Server routers
        path('cas/', include('cas_server.urls', namespace="cas_server")),
    ]

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
