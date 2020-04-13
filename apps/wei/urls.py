# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import WEIListView, WEICreateView, WEIDetailView, WEIUpdateView,\
    BusCreateView, BusManageView, BusUpdateView, BusTeamCreateView,\
    WEIRegisterView, WEIUpdateRegistrationView


app_name = 'wei'
urlpatterns = [
    path('list/', WEIListView.as_view(), name="wei_list"),
    path('create/', WEICreateView.as_view(), name="wei_create"),
    path('detail/<int:pk>/', WEIDetailView.as_view(), name="wei_detail"),
    path('update/<int:pk>/', WEIUpdateView.as_view(), name="wei_update"),
    path('add-bus/<int:pk>/', BusCreateView.as_view(), name="add_bus"),
    path('manage-bus/<int:pk>/', BusManageView.as_view(), name="manage_bus"),
    path('update-bus/<int:pk>/', BusUpdateView.as_view(), name="update_bus"),
    path('add-bus-team/<int:pk>/', BusTeamCreateView.as_view(), name="add_team"),
    path('register/<int:wei_pk>/', WEIRegisterView.as_view(), name="wei_register"),
    path('edit-registration/<int:pk>/', WEIUpdateRegistrationView.as_view(), name="wei_update_registration"),
]
