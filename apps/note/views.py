# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django_tables2 import SingleTableView
from django.urls import reverse_lazy
from note_kfet.inputs import AmountInput
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import TransactionTemplateForm
from .models import TemplateCategory, Transaction, TransactionTemplate, RecurrentTransaction, NoteSpecial
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
    extra_context = {"title": _("Transfer money")}

    def get_queryset(self, **kwargs):
        return Transaction.objects.filter(
            PermissionBackend.filter_queryset(self.request.user, Transaction, "view")
        ).order_by("-created_at").all()[:20]

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['amount_widget'] = AmountInput(attrs={"id": "amount"})
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(Transaction).pk
        context['special_polymorphic_ctype'] = ContentType.objects.get_for_model(SpecialTransaction).pk
        context['special_types'] = NoteSpecial.objects\
            .filter(PermissionBackend.filter_queryset(self.request.user, NoteSpecial, "view"))\
            .order_by("special_type").all()

        # Add a shortcut for entry page for open activities
        if "activity" in settings.INSTALLED_APPS:
            from activity.models import Activity
            context["activities_open"] = Activity.objects.filter(open=True).filter(
                PermissionBackend.filter_queryset(self.request.user, Activity, "view")).filter(
                PermissionBackend.filter_queryset(self.request.user, Activity, "change")).all()

        return context


class TransactionTemplateCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Transaction template
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    success_url = reverse_lazy('note:template_list')
    extra_context = {"title": _("Create new button")}


class TransactionTemplateListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List Transaction templates
    """
    model = TransactionTemplate
    table_class = ButtonTable
    extra_context = {"title": _("Search button")}

    def get_queryset(self, **kwargs):
        """
        Filter the user list with the given pattern.
        """
        qs = super().get_queryset().distinct()
        if "search" in self.request.GET:
            pattern = self.request.GET["search"]
            qs = qs.filter(Q(name__iregex="^" + pattern) | Q(destination__club__name__iregex="^" + pattern))

        qs = qs.order_by('-display', 'category__name', 'destination__club__name', 'name')

        return qs


class TransactionTemplateUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update Transaction template
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    success_url = reverse_lazy('note:template_list')
    extra_context = {"title": _("Update button")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "logs" in settings.INSTALLED_APPS:
            from logs.models import Changelog
            update_logs = Changelog.objects.filter(
                model=ContentType.objects.get_for_model(TransactionTemplate),
                instance_pk=self.object.pk,
                action="edit",
            )
            price_history = []
            for log in update_logs.all():
                old_dict = json.loads(log.previous)
                new_dict = json.loads(log.data)
                old_price = old_dict["amount"]
                new_price = new_dict["amount"]
                if old_price != new_price:
                    price_history.append(dict(price=old_price, time=log.timestamp))

            price_history.append(dict(price=self.object.amount, time=None))

            price_history.reverse()

            context["price_history"] = price_history

        return context


class ConsoView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    The Magic View that make people pay their beer and burgers.
    (Most of the magic happens in the dark world of Javascript see consos.js)
    """
    model = Transaction
    template_name = "note/conso_form.html"
    extra_context = {"title": _("Consumptions")}

    # Transaction history table
    table_class = HistoryTable

    def get_queryset(self, **kwargs):
        return Transaction.objects.filter(
            PermissionBackend.filter_queryset(self.request.user, Transaction, "view")
        ).order_by("-created_at").all()[:20]

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        categories = TemplateCategory.objects.order_by('name').all()
        for category in categories:
            category.templates_filtered = category.templates.filter(
                PermissionBackend().filter_queryset(self.request.user, TransactionTemplate, "view")
            ).filter(display=True).order_by('name').all()
        context['categories'] = [cat for cat in categories if cat.templates_filtered]
        context['highlighted'] = TransactionTemplate.objects.filter(highlighted=True).filter(
            PermissionBackend().filter_queryset(self.request.user, TransactionTemplate, "view")
        ).order_by('name').all()
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(RecurrentTransaction).pk

        # select2 compatibility
        context['no_cache'] = True

        return context
