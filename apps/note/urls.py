# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views
from .models import Note

app_name = 'note'
urlpatterns = [
    path('transfer/', views.TransactionCreateView.as_view(), name='transfer'),
    path('buttons/create/', views.TransactionTemplateCreateView.as_view(), name='template_create'),
    path('buttons/update/<int:pk>/', views.TransactionTemplateUpdateView.as_view(), name='template_update'),
    path('buttons/', views.TransactionTemplateListView.as_view(), name='template_list'),
    path('consos/', views.ConsoView.as_view(), name='consos'),
]
