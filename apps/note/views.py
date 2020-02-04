# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from .models import Transaction,TransactionCategory,TransactionTemplate
from .forms import TransactionTemplateForm, ConsoForm

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
    form_class = TransactionTemplateForm

class ConsoView(LoginRequiredMixin,CreateView):
    """
    Consume
    """
    model = Transaction
    template_name = "note/conso_form.html"
    form_class = ConsoForm

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['template_types'] = TransactionCategory.objects.all()

        if 'template_type' not in self.kwargs.keys():
            return context

        template_type = TransactionCategory.objects.filter(name=self.kwargs.get('template_type')).get()
        context['buttons'] = TransactionTemplate.objects.filter(template_type=template_type)
        context['title'] = template_type

        return context

    def get_success_url(self):
        return reverse('note:consos',args=(self.kwargs.get('template_type'),))
