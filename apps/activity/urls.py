# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views

app_name = 'activity'

urlpatterns = [
    path('', views.ActivityListView.as_view(), name='activity_list'),
    path('<int:pk>/', views.ActivityDetailView.as_view(), name='activity_detail'),
    path('<int:pk>/invite/', views.ActivityInviteView.as_view(), name='activity_invite'),
    path('<int:pk>/entry/', views.ActivityEntryView.as_view(), name='activity_entry'),
    path('<int:pk>/update/', views.ActivityUpdateView.as_view(), name='activity_update'),
    path('new/', views.ActivityCreateView.as_view(), name='activity_create'),
    path('calendar.ics', views.CalendarView.as_view(), name='calendar_ics'),
]
