# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from member.views import CustomLoginView

urlpatterns = [
    # Dev so redirect to something random
    path('', RedirectView.as_view(pattern_name='note:transfer'), name='index'),

    # Include project routers
    path('note/', include('note.urls')),

    # Include Django Contrib and Core routers
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('member.urls')),
    path('accounts/login/', CustomLoginView.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),
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
        path('accounts/login/cas/', cas_views.login, name='cas_login'),
        path('accounts/logout/cas/', cas_views.logout, name='cas_logout'),
       
    ]
if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
