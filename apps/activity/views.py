# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.utils.translation import gettext_lazy as _
from django_tables2.views import SingleTableView

from .forms import ActivityForm, GuestForm
from .models import Activity, Guest
from .tables import ActivityTable


class ActivityCreateView(LoginRequiredMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    success_url = reverse_lazy('activity:activity_list')


class ActivityListView(LoginRequiredMixin, SingleTableView):
    model = Activity
    table_class = ActivityTable

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['title'] = _("Upcoming activities")

        return ctx


class ActivityDetailView(LoginRequiredMixin, DetailView):
    model = Activity


class ActivityUpdateView(LoginRequiredMixin, UpdateView):
    model = Activity
    form_class = ActivityForm
    success_url = reverse_lazy('activity:activity_list')


class ActivityInviteView(LoginRequiredMixin, CreateView):
    model = Guest
    form_class = GuestForm
    success_url = reverse_lazy('activity:activity_list')
    template_name = "activity/activity_invite.html"


class ActivityEntryView(LoginRequiredMixin, TemplateView):
    pass
