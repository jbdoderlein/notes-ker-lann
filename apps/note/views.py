# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DetailView
from django_tables2 import SingleTableView
from django.urls import reverse_lazy
from activity.models import Entry
from note_kfet.inputs import AmountInput
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import TransactionTemplateForm, SearchTransactionForm
from .models import TemplateCategory, Transaction, TransactionTemplate, RecurrentTransaction, NoteSpecial, Note
from .models.transactions import SpecialTransaction
from .tables import HistoryTable, ButtonTable


class TransactionCreateView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    View for the creation of Transaction between two note which are not :models:`transactions.RecurrentTransaction`.
    e.g. for donation/transfer between people and clubs or for credit/debit with :models:`note.NoteSpecial`
    """
    template_name = "note/transaction_form.html"
    # SingleTableView creates `context["table"]` we will  load it with transaction history
    model = Transaction
    # Transaction history table
    table_class = HistoryTable
    extra_context = {"title": _("Transfer money")}

    def get_queryset(self, **kwargs):
        # retrieves only Transaction that user has the right to see.
        return Transaction.objects.filter(
            PermissionBackend.filter_queryset(self.request, Transaction, "view")
        ).order_by("-created_at").all()[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount_widget'] = AmountInput(attrs={"id": "amount"})
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(Transaction).pk
        context['special_polymorphic_ctype'] = ContentType.objects.get_for_model(SpecialTransaction).pk
        context['special_types'] = NoteSpecial.objects\
            .filter(PermissionBackend.filter_queryset(self.request, NoteSpecial, "view"))\
            .order_by("special_type").all()

        # Add a shortcut for entry page for open activities
        if "activity" in settings.INSTALLED_APPS:
            from activity.models import Activity
            activities_open = Activity.objects.filter(open=True, activity_type__manage_entries=True).filter(
                PermissionBackend.filter_queryset(self.request, Activity, "view")).distinct().all()
            context["activities_open"] = [a for a in activities_open
                                          if PermissionBackend.check_perm(self.request,
                                                                          "activity.add_entry",
                                                                          Entry(activity=a,
                                                                                note=self.request.user.note, ))]

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
            qs = qs.filter(
                Q(name__iregex="^" + pattern)
                | Q(destination__club__name__iregex="^" + pattern)
                | Q(category__name__iregex="^" + pattern)
                | Q(description__iregex=pattern)
            )

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
                if "amount" not in old_dict:
                    # The amount price of the button was not modified in this changelog
                    continue
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
    (Most of the magic happens in the dark world of Javascript see `static/note/js/consos.js`)
    """
    model = Transaction
    template_name = "note/conso_form.html"
    extra_context = {"title": _("Consumptions")}

    # Transaction history table
    table_class = HistoryTable

    def dispatch(self, request, *args, **kwargs):
        # Check that the user is authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        templates = TransactionTemplate.objects.filter(
            PermissionBackend().filter_queryset(self.request, TransactionTemplate, "view")
        )
        if not templates.exists():
            raise PermissionDenied(_("You can't see any button."))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        """
        restrict to the transaction history the user can see.
        """
        return Transaction.objects.filter(
            PermissionBackend.filter_queryset(self.request, Transaction, "view")
        ).order_by("-created_at").all()[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = TemplateCategory.objects.order_by('name').all()
        # for each category, find which transaction templates the user can see.
        for category in categories:
            category.templates_filtered = category.templates.filter(
                PermissionBackend().filter_queryset(self.request, TransactionTemplate, "view")
            ).filter(display=True).order_by('name').all()

        context['categories'] = [cat for cat in categories if cat.templates_filtered]
        # some transactiontemplate are put forward to find them easily
        context['highlighted'] = TransactionTemplate.objects.filter(highlighted=True).filter(
            PermissionBackend().filter_queryset(self.request, TransactionTemplate, "view")
        ).order_by('name').all()
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(RecurrentTransaction).pk

        return context


class TransactionSearchView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    model = Note
    context_object_name = "note"
    template_name = "note/search_transactions.html"
    extra_context = {"title": _("Search transactions")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = SearchTransactionForm(data=self.request.GET if self.request.GET else None)
        context["form"] = form

        form.full_clean()
        data = form.cleaned_data if form.is_valid() else {}

        transactions = Transaction.objects.annotate(total_amount=F("quantity") * F("amount")).filter(
            PermissionBackend.filter_queryset(self.request, Transaction, "view"))\
            .filter(Q(source=self.object) | Q(destination=self.object)).order_by('-created_at')

        if "source" in data and data["source"]:
            transactions = transactions.filter(source_id=data["source"].note_id)
        if "destination" in data and data["destination"]:
            transactions = transactions.filter(destination_id=data["destination"].note_id)
        if "type" in data and data["type"]:
            transactions = transactions.filter(polymorphic_ctype__in=data["type"])
        if "reason" in data and data["reason"]:
            transactions = transactions.filter(reason__iregex=data["reason"])
        if "valid" in data and data["valid"]:
            transactions = transactions.filter(valid=data["valid"])
        if "amount_gte" in data and data["amount_gte"]:
            transactions = transactions.filter(total_amount__gte=data["amount_gte"])
        if "amount_lte" in data and data["amount_lte"]:
            transactions = transactions.filter(total_amount__lte=data["amount_lte"])
        if "created_after" in data and data["created_after"]:
            transactions = transactions.filter(created_at__gte=data["created_after"])
        if "created_before" in data and data["created_before"]:
            transactions = transactions.filter(created_at__lte=data["created_before"])

        table = HistoryTable(transactions)
        table.paginate(per_page=100, page=self.request.GET.get("page", 1))
        context["table"] = table

        return context
