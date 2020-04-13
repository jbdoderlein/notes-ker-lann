# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, CreateView
from django_tables2 import SingleTableView
from member.models import Membership, Club
from member.tables import MembershipTable
from note.models import Transaction, NoteClub
from note.tables import HistoryTable
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .models import WEIClub, WEIRegistration, WEIMembership, Bus, BusTeam
from .forms import WEIForm, WEIRegistrationForm, BusForm, BusTeamForm
from .tables import WEITable, WEIRegistrationTable, BusTable, BusTeamTable


class WEIListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing WEI
    """
    model = WEIClub
    table_class = WEITable


class WEICreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create WEI
    """
    model = WEIClub
    form_class = WEIForm

    def form_valid(self, form):
        form.instance.requires_membership = True
        form.instance.parent_club = Club.objects.get(name="Kfet")
        ret = super().form_valid(form)
        NoteClub.objects.create(club=form.instance)
        return ret

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.pk})


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

        club_member = WEIMembership.objects.filter(
            club=club,
            date_end__gte=datetime.today(),
        ).filter(PermissionBackend.filter_queryset(self.request.user, WEIMembership, "view"))
        membership_table = MembershipTable(data=club_member, prefix="membership-")
        membership_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['member_list'] = membership_table

        WEIRegistrationTable.base_columns["delete"].visible = False
        WEIRegistrationTable.base_columns["validate"].visible = False
        all_registrations = WEIRegistration.objects.filter(
            PermissionBackend.filter_queryset(self.request.user, WEIRegistration, "view"))
        all_registrations_table = WEIRegistrationTable(data=all_registrations, prefix="all-registration-")
        all_registrations_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['all_registrations'] = all_registrations_table

        WEIRegistrationTable.base_columns["delete"].visible = True
        WEIRegistrationTable.base_columns["validate"].visible = True
        pre_registrations = all_registrations.filter(membership=None)
        pre_registrations_table = WEIRegistrationTable(data=pre_registrations, prefix="pre-registration-")
        pre_registrations_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['pre_registrations'] = pre_registrations_table

        buses = Bus.objects.filter(PermissionBackend.filter_queryset(self.request.user, Bus, "view"))\
            .filter(wei=self.object)
        bus_table = BusTable(data=buses, prefix="bus-")
        context['buses'] = bus_table

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


class BusCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Bus
    """
    model = Bus
    form_class = BusForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = WEIClub.objects.get(pk=self.kwargs["pk"])
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["wei"].initial = WEIClub.objects.get(pk=self.kwargs["pk"])
        return form

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:manage_bus", kwargs={"pk": self.object.pk})


class BusUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update Bus
    """
    model = Bus
    form_class = BusForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["wei"].disabled = True
        return form

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:manage_bus", kwargs={"pk": self.object.pk})


class BusManageView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Manage Bus
    """
    model = Bus

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei

        bus = self.object
        teams = BusTeam.objects.filter(PermissionBackend.filter_queryset(self.request.user, BusTeam, "view"))\
            .filter(bus=bus)
        teams_table = BusTeamTable(data=teams, prefix="teams-")
        context["teams"] = teams_table

        return context


class BusTeamCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create BusTeam
    """
    model = BusTeam
    form_class = BusTeamForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bus = Bus.objects.get(pk=self.kwargs["pk"])
        context["club"] = bus.wei
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["bus"].initial = Bus.objects.get(pk=self.kwargs["pk"])
        return form

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:manage_bus", kwargs={"pk": self.object.bus.pk})


class WEIRegisterView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Register to the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["user"].initial = self.request.user
        return form

    def form_valid(self, form):
        form.instance.wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.wei.pk})


class WEIUpdateRegistrationView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update a registration for the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        del form.fields["user"]
        return form

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.wei.pk})
