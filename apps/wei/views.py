# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import subprocess
from datetime import date, timedelta
from tempfile import mkdtemp

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Count
from django.db.models.functions.text import Lower
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, RedirectView, TemplateView
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import BaseFormView, DeleteView
from django_tables2 import SingleTableView
from member.models import Membership, Club
from note.models import Transaction, NoteClub, Alias, SpecialTransaction, NoteSpecial
from note.tables import HistoryTable
from note_kfet.settings import BASE_DIR
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin, ProtectedCreateView

from .forms.registration import WEIChooseBusForm
from .models import WEIClub, WEIRegistration, WEIMembership, Bus, BusTeam, WEIRole
from .forms import WEIForm, WEIRegistrationForm, BusForm, BusTeamForm, WEIMembership1AForm, \
    WEIMembershipForm, CurrentSurvey
from .tables import BusRepartitionTable, BusTable, BusTeamTable, WEITable, WEIRegistrationTable, \
    WEIRegistration1ATable, WEIMembershipTable


class CurrentWEIDetailView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        wei = WEIClub.objects.filter(membership_start__lte=date.today()).order_by('date_start')
        if wei.exists():
            wei = wei.last()
            return reverse_lazy('wei:wei_detail', args=(wei.pk,))
        else:
            return reverse_lazy('wei:wei_list')


class WEIListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing WEI
    """
    model = WEIClub
    table_class = WEITable
    ordering = '-year'
    extra_context = {"title": _("Search WEI")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_wei"] = PermissionBackend.check_perm(self.request, "wei.add_weiclub", WEIClub(
            name="",
            email="weiclub@example.com",
            year=0,
            date_start=date.today(),
            date_end=date.today(),
        ))
        return context


class WEICreateView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Create WEI
    """

    model = WEIClub
    form_class = WEIForm
    extra_context = {"title": _("Create WEI")}

    def get_sample_object(self):
        return WEIClub(
            name="",
            email="weiclub@example.com",
            year=0,
            date_start=date.today(),
            date_end=date.today(),
        )

    @transaction.atomic
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
    extra_context = {"title": _("WEI Detail")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        club = context["club"]

        club_transactions = Transaction.objects.all().filter(Q(source=club.note) | Q(destination=club.note)) \
            .filter(PermissionBackend.filter_queryset(self.request, Transaction, "view")) \
            .order_by('-created_at', '-id')
        history_table = HistoryTable(club_transactions, prefix="history-")
        history_table.paginate(per_page=20, page=self.request.GET.get('history-page', 1))
        context['history_list'] = history_table

        club_member = WEIMembership.objects.filter(
            club=club,
            date_end__gte=date.today(),
        ).filter(PermissionBackend.filter_queryset(self.request, WEIMembership, "view"))
        membership_table = WEIMembershipTable(data=club_member, prefix="membership-")
        membership_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['member_list'] = membership_table

        pre_registrations = WEIRegistration.objects.filter(
            PermissionBackend.filter_queryset(self.request, WEIRegistration, "view")).filter(
            membership=None,
            wei=club
        )
        pre_registrations_table = WEIRegistrationTable(data=pre_registrations, prefix="pre-registration-")
        pre_registrations_table.paginate(per_page=20, page=self.request.GET.get('pre-registration-page', 1))
        context['pre_registrations'] = pre_registrations_table

        my_registration = WEIRegistration.objects.filter(wei=club, user=self.request.user)
        if my_registration.exists():
            my_registration = my_registration.get()
        else:
            my_registration = None
        context["my_registration"] = my_registration

        buses = Bus.objects.filter(PermissionBackend.filter_queryset(self.request, Bus, "view")) \
            .filter(wei=self.object).annotate(count=Count("memberships")).order_by("name")
        bus_table = BusTable(data=buses, prefix="bus-")
        context['buses'] = bus_table

        random_user = User.objects.filter(~Q(wei__wei__in=[club])).first()

        if random_user is None:
            # This case occurs when all users are registered to the WEI.
            # Don't worry, Pikachu never went to the WEI.
            # This bug can arrive only in dev mode.
            context["can_add_first_year_member"] = True
            context["can_add_any_member"] = True
        else:
            # Check if the user has the right to create a registration of a random first year member.
            empty_fy_registration = WEIRegistration(
                wei=club,
                user=random_user,
                first_year=True,
                birth_date="1970-01-01",
                gender="No",
                emergency_contact_name="No",
                emergency_contact_phone="No",
            )
            context["can_add_first_year_member"] = PermissionBackend \
                .check_perm(self.request, "wei.add_weiregistration", empty_fy_registration)

            # Check if the user has the right to create a registration of a random old member.
            empty_old_registration = WEIRegistration(
                wei=club,
                user=User.objects.filter(~Q(wei__wei__in=[club])).first(),
                first_year=False,
                birth_date="1970-01-01",
                gender="No",
                emergency_contact_name="No",
                emergency_contact_phone="No",
            )
            context["can_add_any_member"] = PermissionBackend \
                .check_perm(self.request, "wei.add_weiregistration", empty_old_registration)

        empty_bus = Bus(
            wei=club,
            name="",
        )
        context["can_add_bus"] = PermissionBackend.check_perm(self.request, "wei.add_bus", empty_bus)

        context["not_first_year"] = WEIMembership.objects.filter(user=self.request.user).exists()

        return context


class WEIMembershipsView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List all WEI memberships
    """
    model = WEIMembership
    table_class = WEIMembershipTable
    extra_context = {"title": _("View members of the WEI")}

    def dispatch(self, request, *args, **kwargs):
        self.club = WEIClub.objects.get(pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs).filter(club=self.club).distinct()

        pattern = self.request.GET.get("search", "")

        if not pattern:
            return qs.none()

        qs = qs.filter(
            Q(user__first_name__iregex=pattern)
            | Q(user__last_name__iregex=pattern)
            | Q(user__note__alias__name__iregex="^" + pattern)
            | Q(user__note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
            | Q(bus__name__iregex=pattern)
            | Q(team__name__iregex=pattern)
        )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.club
        context["title"] = _("Find WEI Membership")
        return context


class WEIRegistrationsView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List all non-validated WEI registrations.
    """
    model = WEIRegistration
    table_class = WEIRegistrationTable
    extra_context = {"title": _("View registrations to the WEI")}

    def dispatch(self, request, *args, **kwargs):
        self.club = WEIClub.objects.get(pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs).filter(wei=self.club, membership=None).distinct()

        pattern = self.request.GET.get("search", "")

        if pattern:
            qs = qs.filter(
                Q(user__first_name__iregex=pattern)
                | Q(user__last_name__iregex=pattern)
                | Q(user__note__alias__name__iregex="^" + pattern)
                | Q(user__note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.club
        context["title"] = _("Find WEI Registration")
        return context


class WEIUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update the information of the WEI.
    """
    model = WEIClub
    context_object_name = "club"
    form_class = WEIForm
    extra_context = {"title": _("Update the WEI")}

    def dispatch(self, request, *args, **kwargs):
        wei = self.get_object()
        today = date.today()
        # We can't update a past WEI
        # But we can update it while it is not officially opened
        if today > wei.date_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.pk})


class BusCreateView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Create Bus
    """
    model = Bus
    form_class = BusForm
    extra_context = {"title": _("Create new bus")}

    def get_sample_object(self):
        wei = WEIClub.objects.get(pk=self.kwargs["pk"])
        return Bus(
            wei=wei,
            name="",
        )

    def dispatch(self, request, *args, **kwargs):
        wei = WEIClub.objects.get(pk=self.kwargs["pk"])
        today = date.today()
        # We can't add a bus once the WEI is started
        if today >= wei.date_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

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
    extra_context = {"title": _("Update bus")}

    def dispatch(self, request, *args, **kwargs):
        wei = self.get_object().wei
        today = date.today()
        # We can't update a bus once the WEI is started
        if today >= wei.date_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei
        context["information"] = CurrentSurvey.get_algorithm_class().get_bus_information(self.object)
        self.object.save()
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
    extra_context = {"title": _("Manage bus")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei

        bus = self.object
        teams = BusTeam.objects.filter(PermissionBackend.filter_queryset(self.request, BusTeam, "view")) \
            .filter(bus=bus).annotate(count=Count("memberships")).order_by("name")
        teams_table = BusTeamTable(data=teams, prefix="team-")
        context["teams"] = teams_table

        memberships = WEIMembership.objects.filter(PermissionBackend.filter_queryset(
            self.request, WEIMembership, "view")).filter(bus=bus)
        memberships_table = WEIMembershipTable(data=memberships, prefix="membership-")
        memberships_table.paginate(per_page=20, page=self.request.GET.get("membership-page", 1))
        context["memberships"] = memberships_table

        return context


class BusTeamCreateView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Create BusTeam
    """
    model = BusTeam
    form_class = BusTeamForm
    extra_context = {"title": _("Create new team")}

    def get_sample_object(self):
        bus = Bus.objects.get(pk=self.kwargs["pk"])
        return BusTeam(
            name="",
            bus=bus,
            color=0,
        )

    def dispatch(self, request, *args, **kwargs):
        wei = WEIClub.objects.get(buses__pk=self.kwargs["pk"])
        today = date.today()
        # We can't add a team once the WEI is started
        if today >= wei.date_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

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
        return reverse_lazy("wei:manage_bus_team", kwargs={"pk": self.object.pk})


class BusTeamUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update Bus team
    """
    model = BusTeam
    form_class = BusTeamForm
    extra_context = {"title": _("Update team")}

    def dispatch(self, request, *args, **kwargs):
        wei = self.get_object().bus.wei
        today = date.today()
        # We can't update a bus once the WEI is started
        if today >= wei.date_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

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
    extra_context = {"title": _("Manage WEI team")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bus"] = self.object.bus
        context["club"] = self.object.bus.wei

        memberships = WEIMembership.objects.filter(PermissionBackend.filter_queryset(
            self.request, WEIMembership, "view")).filter(team=self.object)
        memberships_table = WEIMembershipTable(data=memberships, prefix="membership-")
        memberships_table.paginate(per_page=20, page=self.request.GET.get("membership-page", 1))
        context["memberships"] = memberships_table

        return context


class WEIRegister1AView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Register a new user to the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm
    extra_context = {"title": _("Register first year student to the WEI")}

    def get_sample_object(self):
        wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        if "myself" in self.request.path:
            user = self.request.user
        else:
            # To avoid unique validation issues, we use an account that can't join the WEI.
            # In development mode, the note account may not exist, we use a random user (may fail)
            user = User.objects.get(username="note") \
                if User.objects.filter(username="note").exists() else User.objects.first()
        return WEIRegistration(
            wei=wei,
            user=user,
            first_year=True,
            birth_date="1970-01-01",
            gender="No",
            emergency_contact_name="No",
            emergency_contact_phone="No",
        )

    def dispatch(self, request, *args, **kwargs):
        wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        today = date.today()
        # We can't register someone once the WEI is started and before the membership start date
        if today >= wei.date_start or today < wei.membership_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        # Don't register twice
        if 'myself' in self.request.path and not self.request.user.is_anonymous \
                and WEIRegistration.objects.filter(wei=wei, user=self.request.user).exists():
            obj = WEIRegistration.objects.get(wei=wei, user=self.request.user)
            return redirect(reverse_lazy('wei:wei_update_registration', args=(obj.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Register 1A")
        context['club'] = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        if "myself" in self.request.path:
            context["form"].fields["user"].disabled = True
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["user"].initial = self.request.user
        del form.fields["first_year"]
        del form.fields["caution_check"]
        del form.fields["information_json"]
        return form

    @transaction.atomic
    def form_valid(self, form):
        form.instance.wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        form.instance.first_year = True

        if not form.instance.pk:
            # Check if the user is not already registered to the WEI
            if WEIRegistration.objects.filter(wei=form.instance.wei, user=form.instance.user).exists():
                form.add_error('user', _("This user is already registered to this WEI."))
                return self.form_invalid(form)

            # Check if the user can be in her/his first year (yeah, no cheat)
            if WEIRegistration.objects.filter(user=form.instance.user).exists():
                form.add_error('user', _("This user can't be in her/his first year since he/she has already"
                                         " participated to a WEI."))
                return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_survey", kwargs={"pk": self.object.pk})


class WEIRegister2AView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Register an old user to the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm
    extra_context = {"title": _("Register old student to the WEI")}

    def get_sample_object(self):
        wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        if "myself" in self.request.path:
            user = self.request.user
        else:
            # To avoid unique validation issues, we use an account that can't join the WEI.
            # In development mode, the note account may not exist, we use a random user (may fail)
            user = User.objects.get(username="note") \
                if User.objects.filter(username="note").exists() else User.objects.first()
        return WEIRegistration(
            wei=wei,
            user=user,
            first_year=True,
            birth_date="1970-01-01",
            gender="No",
            emergency_contact_name="No",
            emergency_contact_phone="No",
        )

    def dispatch(self, request, *args, **kwargs):
        wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        today = date.today()
        # We can't register someone once the WEI is started and before the membership start date
        if today >= wei.date_start or today < wei.membership_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        # Don't register twice
        if 'myself' in self.request.path and not self.request.user.is_anonymous \
                and WEIRegistration.objects.filter(wei=wei, user=self.request.user).exists():
            obj = WEIRegistration.objects.get(wei=wei, user=self.request.user)
            return redirect(reverse_lazy('wei:wei_update_registration', args=(obj.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Register 2A+")
        context['club'] = WEIClub.objects.get(pk=self.kwargs["wei_pk"])

        if "myself" in self.request.path:
            context["form"].fields["user"].disabled = True

        choose_bus_form = WEIChooseBusForm(self.request.POST if self.request.POST else None)
        choose_bus_form.fields["bus"].queryset = Bus.objects.filter(wei=context["club"]).order_by('name')
        choose_bus_form.fields["team"].queryset = BusTeam.objects.filter(bus__wei=context["club"])\
            .order_by('bus__name', 'name')
        context['membership_form'] = choose_bus_form

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["user"].initial = self.request.user
        if "myself" in self.request.path and self.request.user.profile.soge:
            form.fields["soge_credit"].disabled = True
            form.fields["soge_credit"].help_text = _("You already opened an account in the Société générale.")

        del form.fields["caution_check"]
        del form.fields["first_year"]
        del form.fields["information_json"]

        return form

    @transaction.atomic
    def form_valid(self, form):
        form.instance.wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        form.instance.first_year = False

        if not form.instance.pk:
            # Check if the user is not already registered to the WEI
            if WEIRegistration.objects.filter(wei=form.instance.wei, user=form.instance.user).exists():
                form.add_error('user', _("This user is already registered to this WEI."))
                return self.form_invalid(form)

        choose_bus_form = WEIChooseBusForm(self.request.POST)
        if not choose_bus_form.is_valid():
            return self.form_invalid(form)

        information = form.instance.information
        information["preferred_bus_pk"] = [bus.pk for bus in choose_bus_form.cleaned_data["bus"]]
        information["preferred_bus_name"] = [bus.name for bus in choose_bus_form.cleaned_data["bus"]]
        information["preferred_team_pk"] = [team.pk for team in choose_bus_form.cleaned_data["team"]]
        information["preferred_team_name"] = [team.name for team in choose_bus_form.cleaned_data["team"]]
        information["preferred_roles_pk"] = [role.pk for role in choose_bus_form.cleaned_data["roles"]]
        information["preferred_roles_name"] = [role.name for role in choose_bus_form.cleaned_data["roles"]]
        form.instance.information = information
        form.instance.save()

        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_survey", kwargs={"pk": self.object.pk})


class WEIUpdateRegistrationView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update a registration for the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm
    extra_context = {"title": _("Update WEI Registration")}

    def dispatch(self, request, *args, **kwargs):
        wei = self.get_object().wei
        today = date.today()
        # We can't update a registration once the WEI is started and before the membership start date
        if today >= wei.date_start or today < wei.membership_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei

        if self.object.is_validated:
            membership_form = self.get_membership_form(instance=self.object.membership,
                                                       data=self.request.POST)
            context["membership_form"] = membership_form
        elif not self.object.first_year and PermissionBackend.check_perm(
                self.request, "wei.change_weiregistration_information_json", self.object):
            information = self.object.information
            d = dict(
                bus=Bus.objects.filter(pk__in=information["preferred_bus_pk"]).all(),
                team=BusTeam.objects.filter(pk__in=information["preferred_team_pk"]).all(),
                roles=WEIRole.objects.filter(pk__in=information["preferred_roles_pk"]).all(),
            ) if 'preferred_bus_pk' in information else dict()
            choose_bus_form = WEIChooseBusForm(
                self.request.POST if self.request.POST else d
            )
            choose_bus_form.fields["bus"].queryset = Bus.objects.filter(wei=context["club"])
            choose_bus_form.fields["team"].queryset = BusTeam.objects.filter(bus__wei=context["club"])
            context["membership_form"] = choose_bus_form

        if not self.object.soge_credit and self.object.user.profile.soge:
            form = context["form"]
            form.fields["soge_credit"].disabled = True
            form.fields["soge_credit"].help_text = _("You already opened an account in the Société générale.")

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["user"].disabled = True
        # The auto-json-format may cause issues with the default field remove
        if not PermissionBackend.check_perm(self.request, 'wei.change_weiregistration_information_json', self.object):
            del form.fields["information_json"]
        return form

    def get_membership_form(self, data=None, instance=None):
        membership_form = WEIMembershipForm(data if data else None, instance=instance)
        del membership_form.fields["credit_type"]
        del membership_form.fields["credit_amount"]
        del membership_form.fields["first_name"]
        del membership_form.fields["last_name"]
        del membership_form.fields["bank"]
        for field_name, _field in list(membership_form.fields.items()):
            if not PermissionBackend.check_perm(
                    self.request, "wei.change_weimembership_" + field_name, self.object.membership):
                del membership_form.fields[field_name]
        return membership_form

    @transaction.atomic
    def form_valid(self, form):
        # If the membership is already validated, then we update the bus and the team (and the roles)
        if form.instance.is_validated:
            membership_form = self.get_membership_form(self.request.POST, form.instance.membership)
            if not membership_form.is_valid():
                return self.form_invalid(form)
            membership_form.save()
        # If it is not validated and if this is an old member, then we update the choices
        elif not form.instance.first_year and PermissionBackend.check_perm(
                self.request, "wei.change_weiregistration_information_json", self.object):
            choose_bus_form = WEIChooseBusForm(self.request.POST)
            if not choose_bus_form.is_valid():
                return self.form_invalid(form)
            information = form.instance.information
            information["preferred_bus_pk"] = [bus.pk for bus in choose_bus_form.cleaned_data["bus"]]
            information["preferred_bus_name"] = [bus.name for bus in choose_bus_form.cleaned_data["bus"]]
            information["preferred_team_pk"] = [team.pk for team in choose_bus_form.cleaned_data["team"]]
            information["preferred_team_name"] = [team.name for team in choose_bus_form.cleaned_data["team"]]
            information["preferred_roles_pk"] = [role.pk for role in choose_bus_form.cleaned_data["roles"]]
            information["preferred_roles_name"] = [role.name for role in choose_bus_form.cleaned_data["roles"]]
            form.instance.information = information
            form.instance.save()

        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        if self.object.first_year:
            survey = CurrentSurvey(self.object)
            if not survey.is_complete():
                return reverse_lazy("wei:wei_survey", kwargs={"pk": self.object.pk})
        if PermissionBackend.check_perm(self.request, "wei.add_weimembership", WEIMembership(
            club=self.object.wei,
            user=self.object.user,
            date_start=date.today(),
            date_end=date.today(),
            fee=0,
            registration=self.object,
        )):
            return reverse_lazy("wei:validate_registration", kwargs={"pk": self.object.pk})
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.wei.pk})


class WEIDeleteRegistrationView(ProtectQuerysetMixin, LoginRequiredMixin, DeleteView):
    """
    Delete a non-validated WEI registration
    """
    model = WEIRegistration
    extra_context = {"title": _("Delete WEI registration")}

    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        wei = object.wei
        today = date.today()
        # We can't delete a registration of a past WEI
        if today > wei.membership_end:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))

        if not PermissionBackend.check_perm(self.request, "wei.delete_weiregistration", object):
            raise PermissionDenied(_("You don't have the right to delete this WEI registration."))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei
        return context

    def get_success_url(self):
        return reverse_lazy('wei:wei_detail', args=(self.object.wei.pk,))


class WEIValidateRegistrationView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Validate WEI Registration
    """
    model = WEIMembership
    extra_context = {"title": _("Validate WEI registration")}

    def get_sample_object(self):
        registration = WEIRegistration.objects.get(pk=self.kwargs["pk"])
        return WEIMembership(
            club=registration.wei,
            user=registration.user,
            date_start=date.today(),
            date_end=date.today() + timedelta(days=1),
            fee=0,
            registration=registration,
        )

    def dispatch(self, request, *args, **kwargs):
        wei = WEIRegistration.objects.get(pk=self.kwargs["pk"]).wei
        today = date.today()
        # We can't validate anyone once the WEI is started and before the membership start date
        if today >= wei.date_start or today < wei.membership_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        registration = WEIRegistration.objects.get(pk=self.kwargs["pk"])
        context["registration"] = registration
        survey = CurrentSurvey(registration)
        if survey.information.valid:
            context["suggested_bus"] = survey.information.get_selected_bus()
        context["club"] = registration.wei

        kfet = registration.wei.parent_club
        bde = kfet.parent_club

        context["kfet_member"] = Membership.objects.filter(
            club__name=kfet.name,
            user=registration.user,
            date_start__gte=kfet.membership_start,
        ).exists()
        context["bde_member"] = Membership.objects.filter(
            club__name=bde.name,
            user=registration.user,
            date_start__gte=bde.membership_start,
        ).exists()

        context["fee"] = registration.fee

        form = context["form"]
        if registration.soge_credit:
            form.fields["credit_amount"].initial = registration.fee
        else:
            form.fields["credit_amount"].initial = max(0, registration.fee - registration.user.note.balance)

        return context

    def get_form_class(self):
        registration = WEIRegistration.objects.get(pk=self.kwargs["pk"])
        if registration.first_year and 'sleected_bus_pk' not in registration.information:
            return WEIMembership1AForm
        return WEIMembershipForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        registration = WEIRegistration.objects.get(pk=self.kwargs["pk"])
        form.fields["last_name"].initial = registration.user.last_name
        form.fields["first_name"].initial = registration.user.first_name

        if registration.soge_credit:
            form.fields["credit_type"].disabled = True
            form.fields["credit_type"].initial = NoteSpecial.objects.get(special_type="Virement bancaire")
            form.fields["credit_amount"].disabled = True
            form.fields["last_name"].disabled = True
            form.fields["first_name"].disabled = True
            form.fields["bank"].disabled = True
            form.fields["bank"].initial = "Société générale"

        if 'bus' in form.fields:
            # For 2A+ and hardcoded 1A
            form.fields["bus"].widget.attrs["api_url"] = "/api/wei/bus/?wei=" + str(registration.wei.pk)
            if registration.first_year:
                # Use the results of the survey to fill initial data
                # A first year has no other role than "1A"
                del form.fields["roles"]
                survey = CurrentSurvey(registration)
                if survey.information.valid:
                    form.fields["bus"].initial = survey.information.get_selected_bus()
            else:
                # Use the choice of the member to fill initial data
                information = registration.information
                if "preferred_bus_pk" in information and len(information["preferred_bus_pk"]) == 1:
                    form["bus"].initial = Bus.objects.get(pk=information["preferred_bus_pk"][0])
                if "preferred_team_pk" in information and len(information["preferred_team_pk"]) == 1:
                    form["team"].initial = BusTeam.objects.get(pk=information["preferred_team_pk"][0])
                if "preferred_roles_pk" in information:
                    form["roles"].initial = WEIRole.objects.filter(
                        Q(pk__in=information["preferred_roles_pk"]) | Q(name="Adhérent WEI")
                    ).all()
        return form

    @transaction.atomic
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
        # Force the membership of the clubs BDE and Kfet
        membership._force_renew_parent = True

        fee = club.membership_fee_paid if user.profile.paid else club.membership_fee_unpaid

        kfet = club.parent_club
        bde = kfet.parent_club

        kfet_member = Membership.objects.filter(
            club__name=kfet.name,
            user=registration.user,
            date_start__gte=kfet.membership_start,
        ).exists()
        bde_member = Membership.objects.filter(
            club__name=bde.name,
            user=registration.user,
            date_start__gte=bde.membership_start,
        ).exists()

        if not kfet_member:
            fee += kfet.membership_fee_paid if registration.user.profile.paid else kfet.membership_fee_unpaid
        if not bde_member:
            fee += bde.membership_fee_paid if registration.user.profile.paid else bde.membership_fee_unpaid

        credit_type = form.cleaned_data["credit_type"]
        credit_amount = form.cleaned_data["credit_amount"]
        last_name = form.cleaned_data["last_name"]
        first_name = form.cleaned_data["first_name"]
        bank = form.cleaned_data["bank"]

        if credit_type is None or registration.soge_credit:
            credit_amount = 0

        if not registration.soge_credit and user.note.balance + credit_amount < fee:
            # Users must have money before registering to the WEI.
            form.add_error('bus',
                           _("This user don't have enough money to join this club, and can't have a negative balance."))
            return super().form_invalid(form)

        if credit_amount:
            if not last_name:
                form.add_error('last_name', _("This field is required."))
                return super().form_invalid(form)

            if not first_name:
                form.add_error('first_name', _("This field is required."))
                return super().form_invalid(form)

            # Credit note before adding the membership
            SpecialTransaction.objects.create(
                source=credit_type,
                destination=registration.user.note,
                amount=credit_amount,
                reason="Crédit " + str(credit_type) + " (WEI)",
                last_name=last_name,
                first_name=first_name,
                bank=bank,
            )

        # Now, all is fine, the membership can be created.

        if registration.soge_credit:
            form.instance._soge = True

        if registration.first_year:
            membership = form.instance
            # If the user is not a member of the club Kfet, then the membership is created.
            membership.save()
            membership.refresh_from_db()
            membership.roles.set(WEIRole.objects.filter(name="1A").all())
            membership.save()

        membership.save()
        membership.refresh_from_db()
        membership.roles.add(WEIRole.objects.get(name="Adhérent WEI"))

        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.club.pk})


class WEISurveyView(LoginRequiredMixin, BaseFormView, DetailView):
    """
    Display the survey for the WEI for first year members.
    Warning: this page is accessible for anyone that is connected, the view doesn't extend ProtectQuerySetMixin.
    """
    model = WEIRegistration
    template_name = "wei/survey.html"
    survey = None
    extra_context = {"title": _("Survey WEI")}

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj

        wei = obj.wei
        today = date.today()
        # We can't access to the WEI survey once the WEI is started and before the membership start date
        if today >= wei.date_start or today < wei.membership_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))

        if not self.survey:
            self.survey = CurrentSurvey(obj)
        # If the survey is complete, then display the end page.
        if self.survey.is_complete():
            return redirect(reverse_lazy('wei:wei_survey_end', args=(self.survey.registration.pk,)))
        # Non first year members don't have a survey
        if not obj.first_year:
            return redirect(reverse_lazy('wei:wei_survey_end', args=(self.survey.registration.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        """
        Get the survey form. It may depend on the current state of the survey.
        """
        return self.survey.get_form_class()

    def get_form(self, form_class=None):
        """
        Update the form with the data of the survey.
        """
        form = super().get_form(form_class)
        self.survey.update_form(form)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = self.object.wei
        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        Update the survey with the data of the form.
        """
        self.survey.form_valid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('wei:wei_survey', args=(self.get_object().pk,))


class WEISurveyEndView(LoginRequiredMixin, TemplateView):
    template_name = "wei/survey_end.html"
    extra_context = {"title": _("Survey WEI")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = WEIRegistration.objects.get(pk=self.kwargs["pk"]).wei
        return context


class WEIClosedView(LoginRequiredMixin, TemplateView):
    template_name = "wei/survey_closed.html"
    extra_context = {"title": _("Survey WEI")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = WEIClub.objects.get(pk=self.kwargs["pk"])
        return context


class MemberListRenderView(LoginRequiredMixin, View):
    """
    Render Invoice as a generated PDF with the given information and a LaTeX template
    """

    def get_queryset(self, **kwargs):
        qs = WEIMembership.objects.filter(PermissionBackend.filter_queryset(self.request, WEIMembership, "view"))
        qs = qs.filter(club__pk=self.kwargs["wei_pk"]).order_by(
            Lower('bus__name'),
            Lower('team__name'),
            'user__profile__promotion',
            Lower('user__last_name'),
            Lower('user__first_name'),
            'id',
        )

        if "bus_pk" in self.kwargs:
            qs = qs.filter(bus__pk=self.kwargs["bus_pk"])

        if "team_pk" in self.kwargs:
            qs = qs.filter(team__pk=self.kwargs["team_pk"] if self.kwargs["team_pk"] else None)

        return qs.distinct()

    def get(self, request, **kwargs):
        qs = self.get_queryset()

        wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        bus = team = None
        if "bus_pk" in self.kwargs:
            bus = Bus.objects.get(pk=self.kwargs["bus_pk"])
        if "team_pk" in self.kwargs:
            team = BusTeam.objects.filter(pk=self.kwargs["team_pk"] if self.kwargs["team_pk"] else None)
            if team.exists():
                team = team.get()
                bus = team.bus
            else:
                team = dict(name="Staff")

        # Fill the template with the information
        tex = render_to_string("wei/weilist_sample.tex", dict(memberships=qs.all(), wei=wei, bus=bus, team=team))

        try:
            os.mkdir(BASE_DIR + "/tmp")
        except FileExistsError:
            pass
        # We render the file in a temporary directory
        tmp_dir = mkdtemp(prefix=BASE_DIR + "/tmp/")

        try:
            with open("{}/wei-list.tex".format(tmp_dir), "wb") as f:
                f.write(tex.encode("UTF-8"))
            del tex

            with open(os.devnull, "wb") as devnull:
                error = subprocess.Popen(
                    ["/usr/bin/xelatex", "-interaction=nonstopmode", "{}/wei-list.tex".format(tmp_dir)],
                    cwd=tmp_dir,
                    stderr=devnull,
                    stdout=devnull,
                ).wait()

            if error:
                with open("{}/wei-list.log".format(tmp_dir), "r") as f:
                    log = f.read()
                raise IOError("An error attempted while generating a WEI list (code=" + str(error) + ")\n\n" + log)

            # Display the generated pdf as a HTTP Response
            with open("{}/wei-list.pdf".format(tmp_dir), 'rb') as f:
                pdf = f.read()
            response = HttpResponse(pdf, content_type="application/pdf")
            response['Content-Disposition'] = "inline;filename=Liste%20des%20participants%20au%20WEI.pdf"
        except IOError as e:
            raise e
        finally:
            # Delete all temporary files
            shutil.rmtree(tmp_dir)

        return response


class WEI1AListView(LoginRequiredMixin, ProtectQuerysetMixin, SingleTableView):
    model = WEIRegistration
    template_name = "wei/1A_list.html"
    table_class = WEIRegistration1ATable
    extra_context = {"title": _("Attribute buses to first year members")}

    def dispatch(self, request, *args, **kwargs):
        self.club = WEIClub.objects.get(pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, filter_permissions=True, **kwargs):
        qs = super().get_queryset(filter_permissions, **kwargs)
        qs = qs.filter(first_year=True, membership__isnull=False)
        qs = qs.order_by('-membership__bus')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = self.club
        context['bus_repartition_table'] = BusRepartitionTable(Bus.objects.filter(wei=self.club, size__gt=0).all())
        return context


class WEIAttributeBus1AView(ProtectQuerysetMixin, DetailView):
    model = WEIRegistration
    template_name = "wei/attribute_bus_1A.html"
    extra_context = {"title": _("Attribute bus")}

    def get_queryset(self, filter_permissions=True, **kwargs):
        qs = super().get_queryset(filter_permissions, **kwargs)
        qs = qs.filter(first_year=True)
        return qs

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if 'selected_bus_pk' not in obj.information:
            return redirect(reverse_lazy('wei:wei_survey', args=(obj.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = self.object.wei
        context['survey'] = CurrentSurvey(self.object)
        return context


class WEIAttributeBus1ANextView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        wei = WEIClub.objects.filter(pk=self.kwargs['pk'])
        if not wei.exists():
            raise Http404
        wei = wei.get()
        qs = WEIRegistration.objects.filter(wei=wei, membership__isnull=False, membership__bus__isnull=True)
        qs = qs.filter(information_json__contains='selected_bus_pk')  # not perfect, but works...
        if qs.exists():
            return reverse_lazy('wei:wei_bus_1A', args=(qs.first().pk, ))
        return reverse_lazy('wei_1A_list', args=(wei.pk, ))
