# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import BillingListView

app_name = 'treasury'
urlpatterns = [
    path('billing/', BillingListView.as_view(), name='billing'),
]
