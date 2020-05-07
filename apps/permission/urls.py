# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path
from permission.views import RightsView

app_name = 'permission'
urlpatterns = [
    path('rights', RightsView.as_view(), name="rights"),
]
