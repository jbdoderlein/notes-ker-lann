# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django_tables2 import SingleTableView
from member.models import Membership
from member.tables import MembershipTable
from note.models import Transaction
from note.tables import HistoryTable
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .models import WEIClub
from .forms import WEIForm
from .tables import WEITable


class WEIListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing WEI
    """
    model = WEIClub
    table_class = WEITable


class WEIDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    View WEI information
    """
    model = WEIClub
    context_object_name = "club"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        club = context["club"]
        if PermissionBackend.check_perm(self.request.user, "member.change_club_membership_start", club):
            club.update_membership_dates()

        club_transactions = Transaction.objects.all().filter(Q(source=club.note) | Q(destination=club.note)) \
            .filter(PermissionBackend.filter_queryset(self.request.user, Transaction, "view")).order_by('-id')
        history_table = HistoryTable(club_transactions, prefix="history-")
        history_table.paginate(per_page=20, page=self.request.GET.get('history-page', 1))
        context['history_list'] = history_table
        club_member = Membership.objects.filter(
            club=club,
            date_end__gte=datetime.today(),
        ).filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view"))

        membership_table = MembershipTable(data=club_member, prefix="membership-")
        membership_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['member_list'] = membership_table

        # Check if the user has the right to create a membership, to display the button.
        empty_membership = Membership(
            club=club,
            user=User.objects.first(),
            date_start=datetime.now().date(),
            date_end=datetime.now().date(),
            fee=0,
        )
        context["can_add_members"] = PermissionBackend() \
            .has_perm(self.request.user, "member.add_membership", empty_membership)

        return context


class WEIUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update the information of the WEI.
    """
    model = WEIClub
    context_object_name = "club"
    form_class = WEIForm

    def get_success_url(self):
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.pk})
