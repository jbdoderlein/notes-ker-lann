# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views

app_name = 'member'
urlpatterns = [
    path('signup/', views.UserCreateView.as_view(), name="signup"),

    path('club/', views.ClubListView.as_view(), name="club_list"),
    path('club/create/', views.ClubCreateView.as_view(), name="club_create"),
    path('club/<int:pk>/', views.ClubDetailView.as_view(), name="club_detail"),
    path('club/<int:pk>/add_member/', views.ClubAddMemberView.as_view(), name="club_add_member"),
    path('club/manage_roles/<int:pk>/', views.ClubManageRolesView.as_view(), name="club_manage_roles"),
    path('club/renew_membership/<int:pk>/', views.ClubRenewMembershipView.as_view(), name="club_renew_membership"),
    path('club/<int:pk>/update/', views.ClubUpdateView.as_view(), name="club_update"),
    path('club/<int:pk>/update_pic/', views.ClubPictureUpdateView.as_view(), name="club_update_pic"),
    path('club/<int:pk>/aliases/', views.ClubAliasView.as_view(), name="club_alias"),

    path('user/', views.UserListView.as_view(), name="user_list"),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name="user_detail"),
    path('user/<int:pk>/update/', views.UserUpdateView.as_view(), name="user_update_profile"),
    path('user/<int:pk>/update_pic/', views.ProfilePictureUpdateView.as_view(), name="user_update_pic"),
    path('user/<int:pk>/aliases/', views.ProfileAliasView.as_view(), name="user_alias"),
    path('manage-auth-token/', views.ManageAuthTokens.as_view(), name='auth_token'),
]
