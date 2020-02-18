# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from .models import Note, Transaction, TransactionCategory, TransactionTemplate, Alias
from .forms import TransactionForm, TransactionTemplateForm, ConsoForm


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

    def get_form(self, form_class=None):
        """
        If the user has no right to transfer funds, then it won't have the choice of the source of the transfer.
        """
        form = super().get_form(form_class)

        if False:  # TODO: fix it with "if %user has no right to transfer funds"
            del form.fields['source']

        return form

    def form_valid(self, form):
        """
        If the user has no right to transfer funds, then it will be the source of the transfer by default.
        """
        if False:  # TODO: fix it with "if %user has no right to transfer funds"
            form.instance.source = self.request.user.note

        return super().form_valid(form)


class NoteAutocomplete(autocomplete.Select2QuerySetView):
    """
    Auto complete note by aliases
    """
    def get_queryset(self):
        """
        Quand une personne cherche un alias, une requête est envoyée sur l'API dédiée à l'auto-complétion.
        Cette fonction récupère la requête, et renvoie la liste filtrée des aliases.
        """
        #  Un utilisateur non connecté n'a accès à aucune information
        if not self.request.user.is_authenticated:
            return Alias.objects.none()

        qs = Alias.objects.all()

        # self.q est le paramètre de la recherche
        if self.q:
            qs = qs.filter(Q(name__regex=self.q) | Q(normalized_name__regex=Alias.normalize(self.q)))\
                .order_by('normalized_name').distinct()

        # Filtrage par type de note (user, club, special)
        note_type = self.forwarded.get("note_type", None)
        if note_type:
            l = str(note_type).lower()
            if "user" in l:
                qs = qs.filter(note__polymorphic_ctype__model="noteuser")
            elif "club" in l:
                qs = qs.filter(note__polymorphic_ctype__model="noteclub")
            elif "special" in l:
                qs = qs.filter(note__polymorphic_ctype__model="notespecial")
            else:
                qs = qs.none()

        return qs

    def get_result_label(self, result):
        # Gère l'affichage de l'alias dans la recherche
        res = result.name
        note_name = str(result.note)
        if res != note_name:
            res += " (aka. " + note_name + ")"
        return res

    def get_result_value(self, result):
        # Le résultat renvoyé doit être l'identifiant de la note, et non de l'alias
        return str(result.note.pk)


class TransactionTemplateCreateView(LoginRequiredMixin, CreateView):
    """
    Create TransactionTemplate
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm


class TransactionTemplateListView(LoginRequiredMixin, ListView):
    """
    List TransactionsTemplates
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm


class TransactionTemplateUpdateView(LoginRequiredMixin, UpdateView):
    """
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm


class ConsoView(LoginRequiredMixin, CreateView):
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

        template_type = TransactionCategory.objects.filter(
            name=self.kwargs.get('template_type')).get()
        context['buttons'] = TransactionTemplate.objects.filter(
            template_type=template_type)
        context['title'] = template_type

        return context

    def get_success_url(self):
        return reverse('note:consos',
                       args=(self.kwargs.get('template_type'), ))
