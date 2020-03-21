# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import BillingCreateView, BillingListView, BillingUpdateView, BillingRenderView

app_name = 'treasury'
urlpatterns = [
    path('billing/', BillingListView.as_view(), name='billing'),
    path('billing/create/', BillingCreateView.as_view(), name='billing_create'),
    path('billing/<int:pk>/', BillingUpdateView.as_view(), name='billing_update'),
    path('billing/render/<int:pk>/', BillingRenderView.as_view(), name='billing_render'),
]
