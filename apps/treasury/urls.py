# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import InvoiceCreateView, InvoiceListView, InvoiceUpdateView, InvoiceRenderView, RemittanceListView,\
    RemittanceCreateView, RemittanceUpdateView

app_name = 'treasury'
urlpatterns = [
    path('invoice/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoice/create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoice/<int:pk>/', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoice/render/<int:pk>/', InvoiceRenderView.as_view(), name='invoice_render'),

    path('remittance/', RemittanceListView.as_view(), name='remittance_list'),
    path('remittance/create/', RemittanceCreateView.as_view(), name='remittance_create'),
    path('remittance/<int:pk>/', RemittanceUpdateView.as_view(), name='remittance_update'),
]
