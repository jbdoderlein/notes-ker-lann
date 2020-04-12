# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import WEIListView, WEICreateView, WEIDetailView, WEIUpdateView, WEIRegisterView, WEIUpdateRegistrationView


app_name = 'wei'
urlpatterns = [
    path('list/', WEIListView.as_view(), name="wei_list"),
    path('create/', WEICreateView.as_view(), name="wei_create"),
    path('detail/<int:pk>/', WEIDetailView.as_view(), name="wei_detail"),
    path('update/<int:pk>/', WEIUpdateView.as_view(), name="wei_update"),
    path('register/<int:wei_pk>/', WEIRegisterView.as_view(), name="wei_register"),
    path('edit_registration/<int:pk>/', WEIUpdateRegistrationView.as_view(), name="wei_update_registration"),
]
