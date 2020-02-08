# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views
from .models import Note

app_name = 'note'
urlpatterns = [
    path('transfer/', views.TransactionCreate.as_view(), name='transfer'),
    path('buttons/create/',views.TransactionTemplateCreateView.as_view(),name='template_create'),
    path('buttons/update/<int:pk>/',views.TransactionTemplateUpdateView.as_view(),name='template_update'),
    path('buttons/',views.TransactionTemplateListView.as_view(),name='template_list'),

    # API for the note autocompleter
    path('note-autocomplete/', views.NoteAutocomplete.as_view(model=Note),name='note_autocomplete'),
]
