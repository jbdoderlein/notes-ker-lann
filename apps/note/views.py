# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django_tables2 import SingleTableView
from django.urls import reverse_lazy
from note_kfet.inputs import AmountInput
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import TransactionTemplateForm
from .models import Transaction, TransactionTemplate, RecurrentTransaction, NoteSpecial
from .models.transactions import SpecialTransaction
from .tables import HistoryTable, ButtonTable


class TransactionCreateView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    View for the creation of Transaction between two note which are not :models:`transactions.RecurrentTransaction`.
    e.g. for donation/transfer between people and clubs or for credit/debit with :models:`note.NoteSpecial`
    """
    template_name = "note/transaction_form.html"

    model = Transaction
    # Transaction history table
    table_class = HistoryTable

    def get_queryset(self, **kwargs):
        return super().get_queryset(**kwargs).order_by("-id").all()[:20]

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Transfer money')
        context['amount_widget'] = AmountInput(attrs={"id": "amount"})
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(Transaction).pk
        context['special_polymorphic_ctype'] = ContentType.objects.get_for_model(SpecialTransaction).pk
        context['special_types'] = NoteSpecial.objects\
            .filter(PermissionBackend.filter_queryset(self.request.user, NoteSpecial, "view"))\
            .order_by("special_type").all()

        if "activity" in settings.INSTALLED_APPS:
            from activity.models import Activity
            context["activities_open"] = Activity.objects.filter(open=True).filter(
                PermissionBackend.filter_queryset(self.request.user, Activity, "view")).filter(
                PermissionBackend.filter_queryset(self.request.user, Activity, "change")).all()

        return context


class TransactionTemplateCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create TransactionTemplate
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    success_url = reverse_lazy('note:template_list')


class TransactionTemplateListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List TransactionsTemplates
    """
    model = TransactionTemplate
    table_class = ButtonTable


class TransactionTemplateUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    success_url = reverse_lazy('note:template_list')


class ConsoView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    The Magic View that make people pay their beer and burgers.
    (Most of the magic happens in the dark world of Javascript see consos.js)
    """
    model = Transaction
    template_name = "note/conso_form.html"

    # Transaction history table
    table_class = HistoryTable

    def get_queryset(self, **kwargs):
        return super().get_queryset(**kwargs).order_by("-id").all()[:20]

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
