# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import View
from django_tables2 import SingleTableView

from .models import Billing
from .tables import BillingTable


class BillingCreateView(LoginRequiredMixin, CreateView):
    """
    Create Billing
    """
    model = Billing
    fields = '__all__'
    # form_class = ClubForm


class BillingListView(LoginRequiredMixin, SingleTableView):
    """
    List existing Billings
    """
    model = Billing
    table_class = BillingTable


class BillingUpdateView(LoginRequiredMixin, UpdateView):
    """
    Create Billing
    """
    model = Billing
    fields = '__all__'
    # form_class = BillingForm


class BillingRenderView(View):
    """
    Render Billing
    """
