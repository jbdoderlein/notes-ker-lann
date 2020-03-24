# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from .views import InvoiceCreateView, InvoiceListView, InvoiceUpdateView, InvoiceRenderView, RemittanceListView,\
    RemittanceCreateView, RemittanceUpdateView, LinkTransactionToRemittanceView, UnlinkTransactionToRemittanceView

app_name = 'treasury'
urlpatterns = [
    # Invoice app paths
    path('invoice/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoice/create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoice/<int:pk>/', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoice/render/<int:pk>/', InvoiceRenderView.as_view(), name='invoice_render'),

    # Remittance app paths
    path('remittance/', RemittanceListView.as_view(), name='remittance_list'),
    path('remittance/create/', RemittanceCreateView.as_view(), name='remittance_create'),
    path('remittance/<int:pk>/', RemittanceUpdateView.as_view(), name='remittance_update'),
    path('remittance/link_transaction/<int:pk>/', LinkTransactionToRemittanceView.as_view(), name='link_transaction'),
    path('remittance/unlink_transaction/<int:pk>/', UnlinkTransactionToRemittanceView.as_view(),
         name='unlink_transaction'),
]
