# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django_tables2 import SingleTableView
from django.urls import reverse_lazy
from note_kfet.inputs import AmountInput
from permission.backends import PermissionBackend

from .forms import TransactionTemplateForm
from .models import Transaction, TransactionTemplate, Alias, RecurrentTransaction, NoteSpecial
from .models.transactions import SpecialTransaction
from .tables import HistoryTable, ButtonTable


class TransactionCreateView(LoginRequiredMixin, SingleTableView):
    """
    View for the creation of Transaction between two note which are not :models:`transactions.RecurrentTransaction`.
    e.g. for donation/transfer between people and clubs or for credit/debit with :models:`note.NoteSpecial`
    """
    template_name = "note/transaction_form.html"

    model = Transaction
    # Transaction history table
    table_class = HistoryTable
    table_pagination = {"per_page": 50}

    def get_queryset(self):
        return Transaction.objects.filter(PermissionBackend.filter_queryset(
            self.request.user, Transaction, "view")
        ).order_by("-id").all()[:50]

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Transfer money')
        context['amount_widget'] = AmountInput(attrs={"id": "amount"})
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(Transaction).pk
        context['special_polymorphic_ctype'] = ContentType.objects.get_for_model(SpecialTransaction).pk
        context['special_types'] = NoteSpecial.objects.order_by("special_type").all()

        return context


class NoteAutocomplete(autocomplete.Select2QuerySetView):
    """
    Auto complete note by aliases. Used in every search field for note
    ex: :view:`ConsoView`, :view:`TransactionCreateView`
    """

    def get_queryset(self):
        """
        When someone look for an :models:`note.Alias`, a query is sent to the dedicated API.
        This function handles the result and return a filtered list of aliases.
        """
        #  Un utilisateur non connecté n'a accès à aucune information
        if not self.request.user.is_authenticated:
            return Alias.objects.none()

        qs = Alias.objects.all()

        # self.q est le paramètre de la recherche
        if self.q:
            qs = qs.filter(Q(name__regex="^" + self.q) | Q(normalized_name__regex="^" + Alias.normalize(self.q))) \
                .order_by('normalized_name').distinct()

        # Filtrage par type de note (user, club, special)
        note_type = self.forwarded.get("note_type", None)
        if note_type:
            types = str(note_type).lower()
            if "user" in types:
                qs = qs.filter(note__polymorphic_ctype__model="noteuser")
            elif "club" in types:
                qs = qs.filter(note__polymorphic_ctype__model="noteclub")
            elif "special" in types:
                qs = qs.filter(note__polymorphic_ctype__model="notespecial")
            else:
                qs = qs.none()

        return qs

    def get_result_label(self, result):
        """
        Show the selected alias and the username associated
        <Alias> (aka. <Username> )
        """
        # Gère l'affichage de l'alias dans la recherche
        res = result.name
        note_name = str(result.note)
        if res != note_name:
            res += " (aka. " + note_name + ")"
        return res

    def get_result_value(self, result):
        """
        The value used for the transactions will be the id of the Note.
        """
        return str(result.note.pk)


class TransactionTemplateCreateView(LoginRequiredMixin, CreateView):
    """
    Create TransactionTemplate
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    success_url = reverse_lazy('note:template_list')


class TransactionTemplateListView(LoginRequiredMixin, SingleTableView):
    """
    List TransactionsTemplates
    """
    model = TransactionTemplate
    table_class = ButtonTable


class TransactionTemplateUpdateView(LoginRequiredMixin, UpdateView):
    """
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    success_url = reverse_lazy('note:template_list')


class ConsoView(LoginRequiredMixin, SingleTableView):
    """
    The Magic View that make people pay their beer and burgers.
    (Most of the magic happens in the dark world of Javascript see consos.js)
    """
    template_name = "note/conso_form.html"

    # Transaction history table
    table_class = HistoryTable
    table_pagination = {"per_page": 50}

    def get_queryset(self):
        return Transaction.objects.filter(
            PermissionBackend.filter_queryset(self.request.user, Transaction, "view")
        ).order_by("-id").all()[:50]

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        from django.db.models import Count
        buttons = TransactionTemplate.objects.filter(
            PermissionBackend().filter_queryset(self.request.user, TransactionTemplate, "view")
        ).filter(display=True).annotate(clicks=Count('recurrenttransaction')).order_by('category__name', 'name')
        context['transaction_templates'] = buttons
        context['most_used'] = buttons.order_by('-clicks', 'name')[:10]
        context['title'] = _("Consumptions")
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(RecurrentTransaction).pk

        # select2 compatibility
        context['no_cache'] = True

        return context
