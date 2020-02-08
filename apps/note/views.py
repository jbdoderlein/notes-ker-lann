# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from .models import Transaction, TransactionTemplate, Note
from .forms import TransactionForm, TransactionTemplateForm

class TransactionCreate(LoginRequiredMixin, CreateView):
    """
    Show transfer page

    TODO: If user have sufficient rights, they can transfer from an other note
    """
    model = Transaction
    form_class = TransactionForm

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Transfer money from your account '
                             'to one or others')
        return context


class NoteAutocomplete(autocomplete.Select2QuerySetView):
    """
    Auto complete note by aliases
    """

    def get_queryset(self):
        """
        Quand une personne cherche un alias, une requête est envoyée sur l'API dédiée à l'auto-complétion.
        Cette fonction récupère la requête, et renvoie la liste filtrée des notes par aliases.
        """
        qs = Note.objects.all()

        if self.q:
            qs = qs.filter(Q(alias__name__regex=self.q) | Q(alias__normalized_name__regex=self.q))

        return qs


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
