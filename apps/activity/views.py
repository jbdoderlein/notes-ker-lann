# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.utils.translation import gettext_lazy as _
from django_tables2.views import SingleTableView

from .forms import ActivityForm
from .models import Activity


class ActivityCreateView(CreateView):
    model = Activity
    form_class = ActivityForm


class ActivityListView(SingleTableView):
    model = Activity

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = _("Upcoming activities")

        return ctx


class ActivityDetailView(DetailView):
    model = Activity


class ActivityUpdateView(UpdateView):
    model = Activity
    form_class = ActivityForm


class ActivityEntryView(TemplateView):
    pass
