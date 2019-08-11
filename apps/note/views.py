# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from .models import Transaction,TransactionTemplate
from .forms import TransactionTemplateForm

class TransactionCreate(LoginRequiredMixin, CreateView):
    """
    Show transfer page

    TODO: If user have sufficient rights, they can transfer from an other note
    """
    model = Transaction
    fields = ('destination', 'amount', 'reason')

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Transfer money from your account '
                             'to one or others')
        return context

class TransactionTemplateCreateView(LoginRequiredMixin,CreateView):
    """
    Create TransactionTemplate
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm

class TransactionTemplateListView(LoginRequiredMixin,ListView):
    """
    List TransactionsTemplates
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm

class TransactionTemplateUpdateView(LoginRequiredMixin,UpdateView):
    """
    """
    model = TransactionTemplate
    form_class=TransactionTemplateForm
