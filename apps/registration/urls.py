# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views

app_name = 'registration'
urlpatterns = [
    path('signup/', views.UserCreateView.as_view(), name="signup"),
    path('validate_email/sent/', views.UserValidationEmailSentView.as_view(), name='email_validation_sent'),
    path('validate_email/resend/<int:pk>/', views.UserResendValidationEmailView.as_view(),
         name='email_validation_resend'),
    path('validate_email/<uidb64>/<token>/', views.UserValidateView.as_view(), name='email_validation'),
    path('validate_user/', views.FutureUserListView.as_view(), name="future_user_list"),
    path('validate_user/<int:pk>/', views.FutureUserDetailView.as_view(), name="future_user_detail"),
    path('validate_user/<int:pk>/invalidate/', views.FutureUserInvalidateView.as_view(), name="future_user_invalidate"),
]
