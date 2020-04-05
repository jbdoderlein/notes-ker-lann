# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views

app_name = 'registration'
urlpatterns = [
    path('signup/', views.UserCreateView.as_view(), name="signup"),
    path('accounts/activate/sent', views.UserActivationEmailSentView.as_view(), name='account_activation_sent'),
    path('accounts/activate/<uidb64>/<token>', views.UserActivateView.as_view(), name='account_activation'),
]
