# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views

app_name = 'member'
urlpatterns = [
    path('signup/', views.UserCreateView.as_view(), name="signup"),
    path('club/', views.ClubListView.as_view(), name="club_list"),
    path('club/<int:pk>/', views.ClubDetailView.as_view(), name="club_detail"),
    path('club/<int:pk>/add_member/', views.ClubAddMemberView.as_view(), name="club_add_member"),
    path('club/create/', views.ClubCreateView.as_view(), name="club_create"),
    path('user/', views.UserListView.as_view(), name="user_list"),
    path('user/<int:pk>', views.UserDetailView.as_view(), name="user_detail"),
    path('user/<int:pk>/update', views.UserUpdateView.as_view(), name="user_update_profile"),
    path('user/<int:pk>/update_pic', views.UserUpdateView.as_view(), name="user_update_pic"),
    path('user/<int:pk>/aliases', views.AliasView.as_view(), name="user_alias"),
    path('user/aliases/delete/<int:pk>', views.DeleteAliasView.as_view(), name="user_alias_delete"),
    path('manage-auth-token/', views.ManageAuthTokens.as_view(), name='auth_token'),
    # API for the user autocompleter
    path('user/user-autocomplete', views.UserAutocomplete.as_view(), name="user_autocomplete"),
]
