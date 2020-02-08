#!/usr/bin/env python

# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views

app_name = 'member'
urlpatterns = [
    path('signup/',views.UserCreateView.as_view(),name="signup"),
    path('club/',views.ClubListView.as_view(),name="club_list"),
    path('club/<int:pk>/',views.ClubDetailView.as_view(),name="club_detail"),
    path('club/<int:pk>/add_member/',views.ClubAddMemberView.as_view(),name="club_add_member"),
    path('club/create/',views.ClubCreateView.as_view(),name="club_create"),
    path('user/',views.UserListView.as_view(),name="user_list"),
    path('user/<int:pk>',views.UserDetailView.as_view(),name="user_detail"),
    path('user/<int:pk>/update',views.UserUpdateView.as_view(),name="user_update_profile"),
    path('user/user-autocomplete',views.UserAutocomplete.as_view(),name="user_autocomplete"),
]
