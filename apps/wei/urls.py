# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import CurrentWEIDetailView, WEIListView, WEICreateView, WEIDetailView, WEIUpdateView,\
    BusCreateView, BusManageView, BusUpdateView, BusTeamCreateView, BusTeamManageView, BusTeamUpdateView,\
    WEIRegister1AView, WEIRegister2AView, WEIUpdateRegistrationView, WEIValidateRegistrationView, WEISurveyView


app_name = 'wei'
urlpatterns = [
    path('detail/', CurrentWEIDetailView.as_view(), name="current_wei_detail"),
    path('list/', WEIListView.as_view(), name="wei_list"),
    path('create/', WEICreateView.as_view(), name="wei_create"),
    path('detail/<int:pk>/', WEIDetailView.as_view(), name="wei_detail"),
    path('update/<int:pk>/', WEIUpdateView.as_view(), name="wei_update"),
    path('add-bus/<int:pk>/', BusCreateView.as_view(), name="add_bus"),
    path('manage-bus/<int:pk>/', BusManageView.as_view(), name="manage_bus"),
    path('update-bus/<int:pk>/', BusUpdateView.as_view(), name="update_bus"),
    path('add-bus-team/<int:pk>/', BusTeamCreateView.as_view(), name="add_team"),
    path('manage-bus-team/<int:pk>/', BusTeamManageView.as_view(), name="manage_bus_team"),
    path('update-bus-team/<int:pk>/', BusTeamUpdateView.as_view(), name="update_bus_team"),
    path('register/<int:wei_pk>/1A/', WEIRegister1AView.as_view(), name="wei_register_1A"),
    path('register/<int:wei_pk>/2A+/', WEIRegister2AView.as_view(), name="wei_register_2A"),
    path('register/<int:wei_pk>/1A/myself/', WEIRegister1AView.as_view(), name="wei_register_1A_myself"),
    path('register/<int:wei_pk>/2A+/myself/', WEIRegister2AView.as_view(), name="wei_register_2A_myself"),
    path('edit-registration/<int:pk>/', WEIUpdateRegistrationView.as_view(), name="wei_update_registration"),
    path('validate/<int:pk>/', WEIValidateRegistrationView.as_view(), name="validate_registration"),
    path('survey/<int:pk>/', WEISurveyView.as_view(), name="wei_survey"),
]
