# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, CreateView, View
from django.utils.translation import gettext_lazy as _
from django_tables2 import SingleTableView
from member.models import Membership, Club
from note.models import Transaction, NoteClub
from note.tables import HistoryTable
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .models import WEIClub, WEIRegistration, WEIMembership, Bus, BusTeam, WEIRole
from .forms import WEIForm, WEIRegistrationForm, BusForm, BusTeamForm, WEIMembershipForm
from .tables import WEITable, WEIRegistrationTable, BusTable, BusTeamTable, WEIMembershipTable


class CurrentWEIDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        wei = WEIClub.objects.order_by('date_start').last()
        return redirect(reverse_lazy('wei:wei_detail', args=(wei.pk,)))


class WEIListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing WEI
    """
    model = WEIClub
    table_class = WEITable
    ordering = '-year'


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
        membership_table = WEIMembershipTable(data=club_member, prefix="membership-")
        membership_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['member_list'] = membership_table

        pre_registrations = WEIRegistration.objects.filter(
            PermissionBackend.filter_queryset(self.request.user, WEIRegistration, "view")).filter(
            membership=None,
            wei=club
        )
        pre_registrations_table = WEIRegistrationTable(data=pre_registrations, prefix="pre-registration-")
        pre_registrations_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['pre_registrations'] = pre_registrations_table

        my_registration = WEIRegistration.objects.filter(wei=club, user=self.request.user)
        if my_registration.exists():
            my_registration = my_registration.get()
        else:
            my_registration = None
        context["my_registration"] = my_registration

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
        context["can_add_members"] = PermissionBackend \
            .check_perm(self.request.user, "member.add_membership", empty_membership)

        empty_bus = Bus(
            wei=club,
            name="",
        )
        context["can_add_bus"] = PermissionBackend.check_perm(self.request.user, "wei.add_bus", empty_bus)

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
        teams_table = BusTeamTable(data=teams, prefix="team-")
        context["teams"] = teams_table

        memberships = WEIMembership.objects.filter(PermissionBackend.filter_queryset(
            self.request.user, WEIMembership, "view")).filter(bus=bus)
        memberships_table = WEIMembershipTable(data=memberships, prefix="membership-")
        memberships_table.paginate(per_page=20, page=self.request.GET.get("membership-page", 1))
        context["memberships"] = memberships_table

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


class BusTeamUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update Bus team
    """
    model = BusTeam
    form_class = BusTeamForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.bus.wei
        context["bus"] = self.object.bus
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["bus"].disabled = True
        return form

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:manage_bus_team", kwargs={"pk": self.object.pk})


class BusTeamManageView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Manage Bus team
    """
    model = BusTeam

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bus"] = self.object.bus
        context["club"] = self.object.bus.wei

        memberships = WEIMembership.objects.filter(PermissionBackend.filter_queryset(
            self.request.user, WEIMembership, "view")).filter(team=self.object)
        memberships_table = WEIMembershipTable(data=memberships, prefix="membership-")
        memberships_table.paginate(per_page=20, page=self.request.GET.get("membership-page", 1))
        context["memberships"] = memberships_table

        return context


class WEIRegister1AView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Register a new user to the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Register 1A")
        context['club'] = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["user"].initial = self.request.user
        del form.fields["first_year"]
        del form.fields["caution_check"]
        return form

    def form_valid(self, form):
        form.instance.wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        form.instance.first_year = True
        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        # TODO Replace it with the link of the survey
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.wei.pk})


class WEIRegister2AView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Register an old user to the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Register 2A+")
        context['club'] = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["user"].initial = self.request.user
        del form.fields["first_year"]
        del form.fields["ml_events_registration"]
        del form.fields["ml_art_registration"]
        del form.fields["ml_sport_registration"]
        return form

    def form_valid(self, form):
        form.instance.wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        form.instance.first_year = False
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if "user" in form.fields:
            del form.fields["user"]
        return form

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.wei.pk})


class WEIValidateRegistrationView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Validate WEI Registration
    """
    model = WEIMembership
    form_class = WEIMembershipForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        registration = WEIRegistration.objects.get(pk=self.kwargs["pk"])
        context["registration"] = registration
        context["club"] = registration.wei
        context["fee"] = registration.wei.membership_fee_paid if registration.user.profile.paid \
            else registration.wei.membership_fee_unpaid
        context["kfet_member"] = Membership.objects.filter(
            club__name="Kfet",
            user=registration.user,
            date_start__lte=datetime.now().date(),
            date_end__gte=datetime.now().date(),
        ).exists()

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if WEIRegistration.objects.get(pk=self.kwargs["pk"]).first_year:
            del form.fields["roles"]
        return form

    def form_valid(self, form):
        """
        Create membership, check that all is good, make transactions
        """
        registration = WEIRegistration.objects.get(pk=self.kwargs["pk"])
        club = registration.wei
        user = registration.user

        membership = form.instance
        membership.user = user
        membership.club = club
        membership.date_start = min(date.today(), club.date_start)
        membership.registration = registration

        if user.profile.paid:
            fee = club.membership_fee_paid
        else:
            fee = club.membership_fee_unpaid

        if not registration.soge_credit and user.note.balance < fee:
            # Users must have money before registering to the WEI.
            # TODO Send a notification to the user (with a mail?) to tell her/him to credit her/his note
            form.add_error('bus',
                           _("This user don't have enough money to join this club, and can't have a negative balance."))
            return super().form_invalid(form)

        if not registration.caution_check and not registration.first_year:
            form.add_error('bus', _("This user didn't give her/his caution check."))
            return super().form_invalid(form)

        if club.parent_club is not None:
            if not Membership.objects.filter(user=form.instance.user, club=club.parent_club).exists():
                form.add_error('user', _('User is not a member of the parent club') + ' ' + club.parent_club.name)
                return super().form_invalid(form)

        # Now, all is fine, the membership can be created.

        if registration.first_year:
            membership = form.instance
            membership.save()
            membership.refresh_from_db()
            membership.roles.set(WEIRole.objects.filter(name="1A").all())
            membership.save()

        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.club.pk})
