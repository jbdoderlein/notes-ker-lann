# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import CurrentWEIDetailView, WEI1AListView, WEIListView, WEICreateView, WEIDetailView, WEIUpdateView, \
    WEIRegistrationsView, WEIMembershipsView, MemberListRenderView, \
    BusCreateView, BusManageView, BusUpdateView, BusTeamCreateView, BusTeamManageView, BusTeamUpdateView, \
    WEIAttributeBus1AView, WEIAttributeBus1ANextView, WEIRegister1AView, WEIRegister2AView, WEIUpdateRegistrationView, \
    WEIDeleteRegistrationView, WEIValidateRegistrationView, WEISurveyView, WEISurveyEndView, WEIClosedView

app_name = 'wei'
urlpatterns = [
    path('detail/', CurrentWEIDetailView.as_view(), name="current_wei_detail"),
    path('list/', WEIListView.as_view(), name="wei_list"),
    path('create/', WEICreateView.as_view(), name="wei_create"),
    path('detail/<int:pk>/', WEIDetailView.as_view(), name="wei_detail"),
    path('update/<int:pk>/', WEIUpdateView.as_view(), name="wei_update"),
    path('detail/<int:pk>/registrations/', WEIRegistrationsView.as_view(), name="wei_registrations"),
    path('detail/<int:pk>/memberships/', WEIMembershipsView.as_view(), name="wei_memberships"),
    path('detail/<int:wei_pk>/memberships/pdf/', MemberListRenderView.as_view(), name="wei_memberships_pdf"),
    path('detail/<int:wei_pk>/memberships/pdf/<int:bus_pk>/', MemberListRenderView.as_view(),
         name="wei_memberships_bus_pdf"),
    path('detail/<int:wei_pk>/memberships/pdf/<int:bus_pk>/<int:team_pk>/', MemberListRenderView.as_view(),
         name="wei_memberships_team_pdf"),
    path('bus-1A/list/<int:pk>/', WEI1AListView.as_view(), name="wei_1A_list"),
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
    path('delete-registration/<int:pk>/', WEIDeleteRegistrationView.as_view(), name="wei_delete_registration"),
    path('validate/<int:pk>/', WEIValidateRegistrationView.as_view(), name="validate_registration"),
    path('survey/<int:pk>/', WEISurveyView.as_view(), name="wei_survey"),
    path('survey/<int:pk>/end/', WEISurveyEndView.as_view(), name="wei_survey_end"),
    path('detail/<int:pk>/closed/', WEIClosedView.as_view(), name="wei_closed"),
    path('bus-1A/<int:pk>/', WEIAttributeBus1AView.as_view(), name="wei_bus_1A"),
    path('bus-1A/next/<int:pk>/', WEIAttributeBus1ANextView.as_view(), name="wei_bus_1A_next"),
]
