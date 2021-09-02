# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.urls import path

from .views import RightsView, ScopesView

app_name = 'permission'
urlpatterns = [
    path('rights/', RightsView.as_view(), name="rights"),
]

if "oauth2_provider" in settings.INSTALLED_APPS:
    urlpatterns += [
        path('scopes/', ScopesView.as_view(), name="scopes"),
    ]
