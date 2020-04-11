# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import WEIListView


app_name = 'wei'
urlpatterns = [
    path('list/', WEIListView.as_view(), name="wei_list"),
]
