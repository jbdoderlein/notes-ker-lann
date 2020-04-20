# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import HiddenInput
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, CreateView, RedirectView, TemplateView
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import BaseFormView
from django_tables2 import SingleTableView
from member.models import Membership, Club
from note.models import Transaction, NoteClub
from note.tables import HistoryTable
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms.registration import WEIChooseBusForm
from .models import WEIClub, WEIRegistration, WEIMembership, Bus, BusTeam, WEIRole
from .forms import WEIForm, WEIRegistrationForm, BusForm, BusTeamForm, WEIMembershipForm, CurrentSurvey
from .tables import WEITable, WEIRegistrationTable, BusTable, BusTeamTable, WEIMembershipTable


class CurrentWEIDetailView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        wei = WEIClub.objects.filter(membership_start__lte=date.today()).order_by('date_start').last()
        return reverse_lazy('wei:wei_detail', args=(wei.pk,))


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

        # Check if the user has the right to create a membership with a random user, to display the button.
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

        context["not_first_year"] = WEIMembership.objects.filter(user=self.request.user).exists()

        return context


class WEIUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update the information of the WEI.
    """
    model = WEIClub
    context_object_name = "club"
    form_class = WEIForm

    def dispatch(self, request, *args, **kwargs):
        wei = self.get_object()
        today = date.today()
        # We can't update a past WEI
        # But we can update it while it is not officially opened
        if today > wei.membership_end:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.pk})


class BusCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Bus
    """
    model = Bus
    form_class = BusForm

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
        return reverse_lazy("wei:manage_bus", kwargs={"pk": self.object.bus.pk})


class BusTeamUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update Bus team
    """
    model = BusTeam
    form_class = BusTeamForm

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

    def dispatch(self, request, *args, **kwargs):
        wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        today = date.today()
        # We can't register someone once the WEI is started and before the membership start date
        if today >= wei.date_start or today < wei.membership_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
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

    def form_valid(self, form):
        form.instance.wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        form.instance.first_year = True
        return super().form_valid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_survey", kwargs={"pk": self.object.pk})


class WEIRegister2AView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Register an old user to the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        today = date.today()
        # We can't register someone once the WEI is started and before the membership start date
        if today >= wei.date_start or today < wei.membership_start:
            return redirect(reverse_lazy('wei:wei_closed', args=(wei.pk,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Register 2A+")
        context['club'] = WEIClub.objects.get(pk=self.kwargs["wei_pk"])

        if "myself" in self.request.path:
            context["form"].fields["user"].disabled = True

        choose_bus_form = WEIChooseBusForm()
        choose_bus_form.fields["bus"].queryset = Bus.objects.filter(wei=context["club"])
        choose_bus_form.fields["team"].queryset = BusTeam.objects.filter(bus__wei=context["club"])
        context['membership_form'] = choose_bus_form

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["user"].initial = self.request.user
        if "myself" in self.request.path and self.request.user.profile.soge:
            form.fields["soge_credit"].disabled = True
            form.fields["soge_credit"].help_text = _("You already opened an account in the Société générale.")

        del form.fields["first_year"]
        del form.fields["ml_events_registration"]
        del form.fields["ml_art_registration"]
        del form.fields["ml_sport_registration"]
        del form.fields["information_json"]

        return form

    def form_valid(self, form):
        form.instance.wei = WEIClub.objects.get(pk=self.kwargs["wei_pk"])
        form.instance.first_year = False

        choose_bus_form = WEIChooseBusForm(self.request.POST)
        if not choose_bus_form.is_valid():
            return self.form_invalid(choose_bus_form)

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

    def form_invalid(self, form):
        print(form.data)
        print(form.cleaned_data)
        return super().form_invalid(form)

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("wei:wei_survey", kwargs={"pk": self.object.pk})


class WEIUpdateRegistrationView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update a registration for the WEI
    """
    model = WEIRegistration
    form_class = WEIRegistrationForm

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
            membership_form = WEIMembershipForm(instance=self.object.membership)
            for field_name, field in membership_form.fields.items():
                if not PermissionBackend.check_perm(
                        self.request.user, "wei.change_membership_" + field_name, self.object.membership):
                    field.widget = HiddenInput()
            context["membership_form"] = membership_form
        elif not self.object.first_year and PermissionBackend.check_perm(
                self.request.user, "wei.change_weiregistration_information_json", self.object):
            choose_bus_form = WEIChooseBusForm(
                dict(
                    bus=Bus.objects.filter(pk__in=self.object.information["preferred_bus_pk"]).all(),
                    team=BusTeam.objects.filter(pk__in=self.object.information["preferred_team_pk"]).all(),
                    roles=WEIRole.objects.filter(pk__in=self.object.information["preferred_roles_pk"]).all(),
                )
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
        del form.fields["user"]
        if not self.object.first_year:
            del form.fields["information_json"]
        return form

    def form_valid(self, form):
        # If the membership is already validated, then we update the bus and the team (and the roles)
        if form.instance.is_validated:
            membership_form = WEIMembershipForm(self.request.POST)
            if not membership_form.is_valid():
                return self.form_invalid(membership_form)
            membership_form.save()
        # If it is not validated and if this is an old member, then we update the choices
        elif not form.instance.first_year and PermissionBackend.check_perm(
                self.request.user, "wei.change_weiregistration_information_json", self.object):
            choose_bus_form = WEIChooseBusForm(self.request.POST)
            if not choose_bus_form.is_valid():
                return self.form_invalid(choose_bus_form)
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
        return reverse_lazy("wei:wei_detail", kwargs={"pk": self.object.wei.pk})


class WEIValidateRegistrationView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Validate WEI Registration
    """
    model = WEIMembership
    form_class = WEIMembershipForm

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
        registration = WEIRegistration.objects.get(pk=self.kwargs["pk"])
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
                form["team"].initial = Bus.objects.get(pk=information["preferred_team_pk"][0])
            if "preferred_roles_pk" in information:
                form["roles"].initial = WEIRole.objects.filter(pk__in=information["preferred_roles_pk"]).all()
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


class WEISurveyView(BaseFormView, DetailView):
    """
    Display the survey for the WEI for first
    """
    model = WEIRegistration
    template_name = "wei/survey.html"
    survey = None

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

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
        context["title"] = _("Survey WEI")
        return context

    def form_valid(self, form):
        """
        Update the survey with the data of the form.
        """
        self.survey.form_valid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('wei:wei_survey', args=(self.get_object().pk,))


class WEISurveyEndView(TemplateView):
    template_name = "wei/survey_end.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = WEIRegistration.objects.get(pk=self.kwargs["pk"]).wei
        context["title"] = _("Survey WEI")
        return context


class WEIClosedView(TemplateView):
    template_name = "wei/survey_closed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club"] = WEIClub.objects.get(pk=self.kwargs["pk"])
        context["title"] = _("Survey WEI")
        return context
