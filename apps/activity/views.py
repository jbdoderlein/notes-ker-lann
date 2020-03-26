# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django_tables2.views import SingleTableView

from .models import Activity


class ActivityCreateView(CreateView):
    model = Activity
    template_name = 'activity_create.html'


class ActivityListView(SingleTableView):
    model = Activity
    template_name = 'activity_list.html'


class ActivityDetailView(DetailView):
    model = Activity
    template_name = 'activty_detail.html'


class ActivityUpdateView(UpdateView):
    model = Activity
    template_name = 'activity_update.html'


class ActivityEntryView(TemplateView):
    pass
