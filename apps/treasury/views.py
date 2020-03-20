# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableView

from .models import Billing
from .tables import BillingTable


class BillingListView(LoginRequiredMixin, SingleTableView):
    """
    List existing Billings
    """
    model = Billing
    table_class = BillingTable
