# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Dev so redirect to something random
    path('', RedirectView.as_view(pattern_name='note:transfer'), name='index'),

    # Include project routers
    path('note/', include('note.urls')),

    # Include Django Contrib and Core routers
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('member.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('logs/', include('logs.urls')),
    path('api/', include('api.urls')),  
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if "cas_server" in settings.INSTALLED_APPS:
    urlpatterns += [
        # Include CAS Server routers
        path('cas/', include('cas_server.urls', namespace="cas_server")),
    ]
if "cas" in settings.INSTALLED_APPS:
    from cas import views as cas_views
    urlpatterns += [
        # Include CAS Client routers
        path('accounts/login/', cas_views.login, name='login'),
        path('accounts/logout/', cas_views.logout, name='logout'),
       
    ]
if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
