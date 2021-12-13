# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta, date

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Q, F
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView, TemplateView
from django.views.generic.edit import FormMixin
from django_tables2.views import SingleTableView
from rest_framework.authtoken.models import Token
from note.models import Alias, NoteUser
from note.models.transactions import Transaction, SpecialTransaction
from note.tables import HistoryTable, AliasTable
from note_kfet.middlewares import _set_current_request
from permission.backends import PermissionBackend
from permission.models import Role
from permission.views import ProtectQuerysetMixin, ProtectedCreateView

from .forms import UserForm, ProfileForm, ImageForm, ClubForm, MembershipForm,\
    CustomAuthenticationForm, MembershipRolesForm
from .models import Club, Membership
from .tables import ClubTable, UserTable, MembershipTable, ClubManagerTable


class CustomLoginView(LoginView):
    """
    Login view, where the user can select its permission mask.
    """
    form_class = CustomAuthenticationForm

    @transaction.atomic
    def form_valid(self, form):
        logout(self.request)
        self.request.user = form.get_user()
        _set_current_request(self.request)
        self.request.session['permission_mask'] = form.cleaned_data['permission_mask'].rank
        return super().form_valid(form)


class UserUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update the user information.
    On this view both `:models:member.User` and `:models:member.Profile` are updated through forms
    """
    model = User
    form_class = UserForm
    template_name = 'member/profile_update.html'
    context_object_name = 'user_object'
    extra_context = {"title": _("Update Profile")}

    profile_form = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context['form']
        form.fields['username'].widget.attrs.pop("autofocus", None)
        form.fields['first_name'].widget.attrs.update({"autofocus": "autofocus"})
        form.fields['first_name'].required = True
        form.fields['last_name'].required = True
        form.fields['email'].required = True
        form.fields['email'].help_text = _("This address must be valid.")

        if PermissionBackend.check_perm(self.request, "member.change_profile", context['user_object'].profile):
            context['profile_form'] = self.profile_form(instance=context['user_object'].profile,
                                                        data=self.request.POST if self.request.POST else None)
            if not self.object.profile.report_frequency:
                del context['profile_form'].fields["last_report"]

        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        Check if ProfileForm is correct
        then check if username is not already taken by someone else or by the user,
        then check if email has changed, and if so ask for new validation.
        """

        profile_form = ProfileForm(
            data=self.request.POST,
            instance=self.object.profile,
        )
        profile_form.full_clean()
        if not profile_form.is_valid():
            return super().form_invalid(form)
        new_username = form.data['username']
        # Check if the new username is not already taken as an alias of someone else.
        note = NoteUser.objects.filter(
            alias__normalized_name=Alias.normalize(new_username))
        if note.exists() and note.get().user != self.object:
            form.add_error('username', _("An alias with a similar name already exists."))
            return super().form_invalid(form)
        # Check if the username is one of user's aliases.
        alias = Alias.objects.filter(name=new_username)
        if not alias.exists():
            similar = Alias.objects.filter(
                normalized_name=Alias.normalize(new_username))
            if similar.exists():
                similar.delete()
        olduser = User.objects.get(pk=form.instance.pk)

        user = form.save(commit=False)

        if olduser.email != user.email:
            # If the user changed her/his email, then it is unvalidated and a confirmation link is sent.
            user.profile.email_confirmed = False
            user.profile.send_email_validation_link()

        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        user.save()

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        url = 'member:user_detail' if self.object.profile.registration_valid else 'registration:future_user_detail'
        return reverse_lazy(url, args=(self.object.id,))


class UserDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Display all information about a user.
    """
    model = User
    context_object_name = "user_object"
    template_name = "member/profile_detail.html"
    extra_context = {"title": _("Profile detail")}

    def get_queryset(self, **kwargs):
        """
        We can't display information of a not registered user.
        """
        return super().get_queryset(**kwargs).filter(profile__registration_valid=True)

    def get_context_data(self, **kwargs):
        """
        Add history of transaction and list of membership of user.
        """
        context = super().get_context_data(**kwargs)
        user = context['user_object']
        context["note"] = user.note
        history_list = \
            Transaction.objects.all().filter(Q(source=user.note) | Q(destination=user.note))\
            .order_by("-created_at")\
            .filter(PermissionBackend.filter_queryset(self.request, Transaction, "view"))
        history_table = HistoryTable(history_list, prefix='transaction-')
        history_table.paginate(per_page=20, page=self.request.GET.get("transaction-page", 1))
        context['history_list'] = history_table

        club_list = Membership.objects.filter(user=user, date_end__gte=date.today() - timedelta(days=15))\
            .filter(PermissionBackend.filter_queryset(self.request, Membership, "view"))\
            .order_by("club__name", "-date_start")
        # Display only the most recent membership
        club_list = club_list.distinct("club__name")\
            if settings.DATABASES["default"]["ENGINE"] == 'django.db.backends.postgresql' else club_list
        membership_table = MembershipTable(data=club_list, prefix='membership-')
        membership_table.paginate(per_page=10, page=self.request.GET.get("membership-page", 1))
        context['club_list'] = membership_table

        # Check permissions to see if the authenticated user can lock/unlock the note
        with transaction.atomic():
            modified_note = NoteUser.objects.get(pk=user.note.pk)
            # Don't log these tests
            modified_note._no_signal = True
            modified_note.is_active = True
            modified_note.inactivity_reason = 'manual'
            context["can_lock_note"] = user.note.is_active and PermissionBackend\
                                           .check_perm(self.request, "note.change_noteuser_is_active", modified_note)
            old_note = NoteUser.objects.select_for_update().get(pk=user.note.pk)
            modified_note.inactivity_reason = 'forced'
            modified_note._force_save = True
            modified_note.save()
            context["can_force_lock"] = user.note.is_active and PermissionBackend\
                .check_perm(self.request, "note.change_note_is_active", modified_note)
            old_note._force_save = True
            old_note._no_signal = True
            old_note.save()
            modified_note.refresh_from_db()
            modified_note.is_active = True
            context["can_unlock_note"] = not user.note.is_active and PermissionBackend\
                .check_perm(self.request, "note.change_note_is_active", modified_note)

        return context


class UserListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    Display user list, with a search bar
    """
    model = User
    table_class = UserTable
    template_name = 'member/user_list.html'
    extra_context = {"title": _("Search user")}

    def get_queryset(self, **kwargs):
        """
        Filter the user list with the given pattern.
        """
        qs = super().get_queryset().annotate(alias=F("note__alias__name"))\
            .annotate(normalized_alias=F("note__alias__normalized_name"))\
            .filter(profile__registration_valid=True)

        # Sqlite doesn't support order by in subqueries
        qs = qs.order_by("username").distinct("username")\
            if settings.DATABASES[qs.db]["ENGINE"] == 'django.db.backends.postgresql' else qs.distinct()

        if "search" in self.request.GET and self.request.GET["search"]:
            pattern = self.request.GET["search"]

            qs = qs.filter(
                username__iregex="^" + pattern
            ).union(
                qs.filter(
                    (Q(alias__iregex="^" + pattern)
                     | Q(normalized_alias__iregex="^" + Alias.normalize(pattern))
                     | Q(last_name__iregex="^" + pattern)
                     | Q(first_name__iregex="^" + pattern)
                     | Q(email__istartswith=pattern))
                    & ~Q(username__iregex="^" + pattern)
                ), all=True)
        else:
            qs = qs.none()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pre_registered_users = User.objects.filter(PermissionBackend.filter_queryset(self.request, User, "view"))\
            .filter(profile__registration_valid=False)
        context["can_manage_registrations"] = pre_registered_users.exists()
        return context


class ProfileAliasView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    View and manage user aliases.
    """
    model = User
    template_name = 'member/profile_alias.html'
    context_object_name = 'user_object'
    extra_context = {"title": _("Note aliases")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = context['object'].note
        context["aliases"] = AliasTable(
            note.alias.filter(PermissionBackend.filter_queryset(self.request, Alias, "view")).distinct()
            .order_by('normalized_name').all())
        context["can_create"] = PermissionBackend.check_perm(self.request, "note.add_alias", Alias(
            note=context["object"].note,
            name="",
            normalized_name="",
        ))
        return context


class PictureUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, FormMixin, DetailView):
    """
    Update profile picture of the user note.
    """
    form_class = ImageForm
    extra_context = {"title": _("Update note picture")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.POST, self.request.FILES)
        return context

    def get_success_url(self):
        """Redirect to profile page after upload"""
        return reverse_lazy('member:user_detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.object = self.get_object()
        return self.form_valid(form) if form.is_valid() else self.form_invalid(form)

    @transaction.atomic
    def form_valid(self, form):
        """Save image to note"""
        image = form.cleaned_data['image']

        # Rename as a PNG or GIF
        extension = image.name.split(".")[-1]
        if extension == "gif":
            image.name = "{}_pic.gif".format(self.object.note.pk)
        else:
            image.name = "{}_pic.png".format(self.object.note.pk)

        # Save
        self.object.note.display_image = image
        self.object.note.save()
        return super().form_valid(form)


class ProfilePictureUpdateView(PictureUpdateView):
    model = User
    template_name = 'member/picture_update.html'
    context_object_name = 'user_object'


class ManageAuthTokens(LoginRequiredMixin, TemplateView):
    """
    Affiche le jeton d'authentification, et permet de le regénérer
    """
    model = Token
    template_name = "member/manage_auth_tokens.html"
    extra_context = {"title": _("Manage auth token")}

    def get(self, request, *args, **kwargs):
        if 'regenerate' in request.GET and Token.objects.filter(user=request.user).exists():
            Token.objects.get(user=self.request.user).delete()
            return redirect(reverse_lazy('member:auth_token') + "?show")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = Token.objects.get_or_create(user=self.request.user)[0]
        return context


# ******************************* #
#              CLUB               #
# ******************************* #


class ClubCreateView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Create Club
    """
    model = Club
    form_class = ClubForm
    success_url = reverse_lazy('member:club_list')
    extra_context = {"title": _("Create new club")}

    def get_sample_object(self):
        return Club(
            name="",
            email="",
        )

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy("member:club_detail", kwargs={"pk": self.object.pk})


class ClubListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing Clubs
    """
    model = Club
    table_class = ClubTable
    extra_context = {"title": _("Search club")}

    def get_queryset(self, **kwargs):
        """
        Filter the user list with the given pattern.
        """
        qs = super().get_queryset().distinct()
        if "search" in self.request.GET:
            pattern = self.request.GET["search"]

            qs = qs.filter(
                Q(name__iregex=pattern)
                | Q(note__alias__name__iregex=pattern)
                | Q(note__alias__normalized_name__iregex=Alias.normalize(pattern))
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_add_club"] = PermissionBackend.check_perm(self.request, "member.add_club", Club(
            name="",
            email="club@example.com",
        ))
        return context


class ClubDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Display details of a club
    """
    model = Club
    context_object_name = "club"
    extra_context = {"title": _("Club detail")}

    def get_context_data(self, **kwargs):
        """
        Add list of managers (peoples with Permission/Roles in this club), history of transactions and members list
        """
        context = super().get_context_data(**kwargs)

        club = context["club"]
        if PermissionBackend.check_perm(self.request, "member.change_club_membership_start", club):
            club.update_membership_dates()
        # managers list
        managers = Membership.objects.filter(club=self.object, roles__name="Bureau de club",
                                             date_start__lte=date.today(), date_end__gte=date.today())\
            .order_by('user__last_name').all()
        context["managers"] = ClubManagerTable(data=managers, prefix="managers-")
        # transaction history
        club_transactions = Transaction.objects.all().filter(Q(source=club.note) | Q(destination=club.note))\
            .filter(PermissionBackend.filter_queryset(self.request, Transaction, "view"))\
            .order_by('-created_at')
        history_table = HistoryTable(club_transactions, prefix="history-")
        history_table.paginate(per_page=20, page=self.request.GET.get('history-page', 1))
        context['history_list'] = history_table
        # member list
        club_member = Membership.objects.filter(
            club=club,
            date_end__gte=date.today() - timedelta(days=15),
        ).filter(PermissionBackend.filter_queryset(self.request, Membership, "view"))\
            .order_by("user__username", "-date_start")
        # Display only the most recent membership
        club_member = club_member.distinct("user__username")\
            if settings.DATABASES["default"]["ENGINE"] == 'django.db.backends.postgresql' else club_member

        membership_table = MembershipTable(data=club_member, prefix="membership-")
        membership_table.paginate(per_page=5, page=self.request.GET.get('membership-page', 1))
        context['member_list'] = membership_table

        # Check if the user has the right to create a membership, to display the button.
        empty_membership = Membership(
            club=club,
            user=User.objects.first(),
            date_start=date.today(),
            date_end=date.today(),
            fee=0,
        )
        context["can_add_members"] = PermissionBackend()\
            .has_perm(self.request.user, "member.add_membership", empty_membership)

        return context


class ClubAliasView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Manage aliases of a club.
    """
    model = Club
    template_name = 'member/club_alias.html'
    context_object_name = 'club'
    extra_context = {"title": _("Note aliases")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = context['object'].note
        context["aliases"] = AliasTable(note.alias.filter(
            PermissionBackend.filter_queryset(self.request, Alias, "view")).distinct().all())
        context["can_create"] = PermissionBackend.check_perm(self.request, "note.add_alias", Alias(
            note=context["object"].note,
            name="",
            normalized_name="",
        ))
        return context


class ClubUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update the information of a club.
    """
    model = Club
    context_object_name = "club"
    form_class = ClubForm
    template_name = "member/club_form.html"
    extra_context = {"title": _("Update club")}

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)

        # Don't update a WEI club through this view
        if "wei" in settings.INSTALLED_APPS:
            qs = qs.filter(weiclub=None)

        return qs

    def get_success_url(self):
        return reverse_lazy("member:club_detail", kwargs={"pk": self.object.pk})


class ClubPictureUpdateView(PictureUpdateView):
    """
    Update the profile picture of a club.
    """
    model = Club
    template_name = 'member/picture_update.html'
    context_object_name = 'club'

    def get_success_url(self):
        return reverse_lazy('member:club_detail', kwargs={'pk': self.object.id})


class ClubAddMemberView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Add a membership to a club.
    """
    model = Membership
    form_class = MembershipForm
    template_name = 'member/add_members.html'
    extra_context = {"title": _("Add new member to the club")}

    def get_sample_object(self):
        if "club_pk" in self.kwargs:
            club = Club.objects.get(pk=self.kwargs["club_pk"])
        else:
            club = Membership.objects.get(pk=self.kwargs["pk"]).club
        return Membership(
            user=self.request.user,
            club=club,
            fee=0,
            date_start=timezone.now(),
            date_end=timezone.now() + timedelta(days=1),
        )

    def get_context_data(self, **kwargs):
        """
        Membership can be created, or renewed
        In case of creation the url is /club/<club_pk>/add_member
        For a renewal it will be `club/renew_membership/<pk>`
        """
        context = super().get_context_data(**kwargs)
        form = context['form']

        if "club_pk" in self.kwargs:  # We create a new membership.
            club = Club.objects.filter(PermissionBackend.filter_queryset(self.request, Club, "view"))\
                .get(pk=self.kwargs["club_pk"], weiclub=None)
            form.fields['credit_amount'].initial = club.membership_fee_paid
            # Ensure that the user is member of the parent club and all its the family tree.
            c = club
            clubs_renewal = []
            additional_fee_renewal = 0
            while c.parent_club is not None:
                c = c.parent_club
                clubs_renewal.append(c)
                additional_fee_renewal += c.membership_fee_paid
            context["clubs_renewal"] = clubs_renewal
            context["additional_fee_renewal"] = additional_fee_renewal

            # If the concerned club is the BDE, then we add the option that Société générale pays the membership.
            if club.name != "BDE":
                del form.fields['soge']
            else:
                fee = 0
                bde = Club.objects.get(name="BDE")
                fee += bde.membership_fee_paid
                kfet = Club.objects.get(name="Kfet")
                fee += kfet.membership_fee_paid
                context["total_fee"] = "{:.02f}".format(fee / 100, )
        else:  # This is a renewal. Fields can be pre-completed.
            context["renewal"] = True

            old_membership = self.get_queryset().get(pk=self.kwargs["pk"])
            club = old_membership.club
            user = old_membership.user

            c = club
            clubs_renewal = []
            additional_fee_renewal = 0
            while c.parent_club is not None:
                c = c.parent_club
                # check if a valid membership exists for the parent club
                if c.membership_start and not Membership.objects.filter(
                        club=c,
                        user=user,
                        date_start__gte=c.membership_start,
                ).exists():
                    clubs_renewal.append(c)
                    additional_fee_renewal += c.membership_fee_paid if user.profile.paid else c.membership_fee_unpaid
            context["clubs_renewal"] = clubs_renewal
            context["additional_fee_renewal"] = additional_fee_renewal

            form.fields['user'].initial = user
            form.fields['user'].disabled = True
            form.fields['date_start'].initial = old_membership.date_end + timedelta(days=1)
            form.fields['credit_amount'].initial = (club.membership_fee_paid if user.profile.paid
                                                    else club.membership_fee_unpaid) + additional_fee_renewal
            form.fields['last_name'].initial = user.last_name
            form.fields['first_name'].initial = user.first_name

            # If this is a renewal of a BDE membership, Société générale can pays, if it has not been already done.
            if (club.name != "BDE" and club.name != "Kfet") or user.profile.soge:
                del form.fields['soge']
            else:
                fee = 0
                bde = Club.objects.get(name="BDE")
                if not Membership.objects.filter(
                    club=bde,
                    user=user,
                    date_start__gte=bde.membership_start,
                ).exists():
                    fee += bde.membership_fee_paid if user.profile.paid else bde.membership_fee_unpaid
                kfet = Club.objects.get(name="Kfet")
                if not Membership.objects.filter(
                    club=kfet,
                    user=user,
                    date_start__gte=bde.membership_start,
                ).exists():
                    fee += kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid
                context["total_fee"] = "{:.02f}".format(fee / 100, )

        context['club'] = club

        return context

    def perform_verifications(self, form, user, club, fee):
        """
        Make some additional verifications to check that the membership can be created.
        :return: True if the form is clean, False if there is an error.
        """
        error = False

        # Retrieve form data
        credit_type = form.cleaned_data["credit_type"]
        credit_amount = form.cleaned_data["credit_amount"]
        soge = form.cleaned_data["soge"] and not user.profile.soge and (club.name == "BDE" or club.name == "Kfet")

        if not credit_type:
            credit_amount = 0

        if not soge and user.note.balance + credit_amount < fee and not Membership.objects.filter(
                club__name="Kfet",
                user=user,
                date_start__lte=date.today(),
                date_end__gte=date.today(),
        ).exists():
            # Users without a valid Kfet membership can't have a negative balance.
            # TODO Send a notification to the user (with a mail?) to tell her/him to credit her/his note
            form.add_error('user',
                           _("This user don't have enough money to join this club, and can't have a negative balance."))
            error = True

        if Membership.objects.filter(
                user=form.instance.user,
                club=club,
                date_start__lte=form.instance.date_start,
                date_end__gte=form.instance.date_start,
        ).exists():
            form.add_error('user', _('User is already a member of the club'))
            error = True

        # Must join the parent club before joining this club, except for the Kfet club where it can be at the same time.
        if club.name != "Kfet" and club.parent_club and not Membership.objects.filter(
                user=form.instance.user,
                club=club.parent_club,
                date_start__gte=club.parent_club.membership_start,
        ).exists():
            form.add_error('user', _('User is not a member of the parent club') + ' ' + club.parent_club.name)
            error = True

        if club.membership_start and form.instance.date_start < club.membership_start:
            form.add_error('user', _("The membership must start after {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_start))
            error = True

        if club.membership_end and form.instance.date_start > club.membership_end:
            form.add_error('user', _("The membership must begin before {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_end))
            error = True

        if credit_amount and not SpecialTransaction.validate_payment_form(form):
            # Check that special information for payment are filled
            error = True

        return not error

    @transaction.atomic
    def form_valid(self, form):
        """
        Create membership, check that all is good, make transactions
        """
        # Get the club that is concerned by the membership
        if "club_pk" in self.kwargs:  # get from url of new membership
            club = Club.objects.filter(PermissionBackend.filter_queryset(self.request, Club, "view")) \
                .get(pk=self.kwargs["club_pk"])
            user = form.instance.user
            old_membership = None
        else:  # get from url for renewal
            old_membership = self.get_queryset().get(pk=self.kwargs["pk"])
            club = old_membership.club
            user = old_membership.user

        form.instance.club = club

        # Get form data
        credit_type = form.cleaned_data["credit_type"]
        # but with this way users can customize their section as they want.
        credit_amount = form.cleaned_data["credit_amount"]
        last_name = form.cleaned_data["last_name"]
        first_name = form.cleaned_data["first_name"]
        bank = form.cleaned_data["bank"]
        soge = form.cleaned_data["soge"] and not user.profile.soge and (club.name == "BDE" or club.name == "Kfet")

        # If Société générale pays, then we store that information but the payment must be controlled by treasurers
        # later. The membership transaction will be invalidated.
        if soge:
            credit_type = None
            form.instance._soge = True

        if credit_type is None:
            credit_amount = 0

        fee = 0
        c = club
        # collect the fees required to be paid
        while c is not None and c.membership_start:
            if not Membership.objects.filter(
                    club=c,
                    user=user,
                    date_start__gte=c.membership_start,
            ).exists():
                fee += c.membership_fee_paid if user.profile.paid else c.membership_fee_unpaid
            c = c.parent_club

        # Make some verifications about the form, and if there is an error, then assume that the form is invalid
        if not self.perform_verifications(form, user, club, fee):
            return self.form_invalid(form)

        # Now, all is fine, the membership can be created.

        if club.name == "BDE" or club.name == "Kfet":
            # When we renew the BDE membership, we update the profile section
            # that should happens at least once a year.
            user.profile.section = user.profile.section_generated
            user.profile._force_save = True
            user.profile.save()

        # Credit note before the membership is created.
        if credit_amount > 0:
            transaction = SpecialTransaction(
                source=credit_type,
                destination=user.note,
                quantity=1,
                amount=credit_amount,
                reason="Crédit " + credit_type.special_type + " (Adhésion " + club.name + ")",
                last_name=last_name,
                first_name=first_name,
                bank=bank,
                valid=True,
            )
            transaction._force_save = True
            transaction.save()

        # Parent club memberships are automatically renewed / created.
        # For example, a Kfet membership creates a BDE membership if it does not exist.
        form.instance._force_renew_parent = True

        ret = super().form_valid(form)

        member_role = Role.objects.filter(Q(name="Adhérent BDE") | Q(name="Membre de club")).all() \
            if club.name == "BDE" else Role.objects.filter(Q(name="Adhérent Kfet") | Q(name="Membre de club")).all() \
            if club.name == "Kfet"else Role.objects.filter(name="Membre de club").all()
        # Set the same roles as before
        if old_membership:
            member_role = member_role.union(old_membership.roles.all())
        form.instance.roles.set(member_role)
        form.instance._force_save = True
        form.instance.save()

        # If Société générale pays, then we assume that this is the BDE membership, and we auto-renew the
        # Kfet membership.
        if soge and club.name == "BDE":
            kfet = Club.objects.get(name="Kfet")
            fee = kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid

            # Get current membership, to get the end date
            old_membership = Membership.objects.filter(
                club=kfet,
                user=user,
            ).order_by("-date_start")

            if not old_membership.filter(date_start__gte=kfet.membership_start).exists():
                # If the membership is not already renewed
                membership = Membership(
                    club=kfet,
                    user=user,
                    fee=fee,
                    date_start=max(old_membership.first().date_end + timedelta(days=1), kfet.membership_start)
                    if old_membership.exists() else form.instance.date_start,
                )
                membership._force_save = True
                membership._soge = True
                membership.save()
                membership.refresh_from_db()
                if old_membership.exists():
                    membership.roles.set(old_membership.get().roles.all())
                membership.roles.set(Role.objects.filter(Q(name="Adhérent Kfet") | Q(name="Membre de club")).all())
                membership.save()

        return ret

    def get_success_url(self):
        return reverse_lazy('member:user_detail', kwargs={'pk': self.object.user.id})


class ClubManageRolesView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Manage the roles of a user in a club
    """
    model = Membership
    form_class = MembershipRolesForm
    template_name = 'member/add_members.html'
    extra_context = {"title": _("Manage roles of an user in the club")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = self.object.club
        context['club'] = club
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        club = self.object.club
        form.fields['roles'].queryset = Role.objects.filter(Q(weirole__isnull=not hasattr(club, 'weiclub'))
                                                            & (Q(for_club__isnull=True) | Q(for_club=club))).all()

        return form

    def get_success_url(self):
        return reverse_lazy('member:user_detail', kwargs={'pk': self.object.user.id})


class ClubMembersListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    model = Membership
    table_class = MembershipTable
    template_name = "member/club_members.html"
    extra_context = {"title": _("Members of the club")}

    def get_queryset(self, **kwargs):
        qs = super().get_queryset().filter(club_id=self.kwargs["pk"])

        if 'search' in self.request.GET:
            pattern = self.request.GET['search']
            qs = qs.filter(
                Q(user__first_name__iregex='^' + pattern)
                | Q(user__last_name__iregex='^' + pattern)
                | Q(user__note__alias__normalized_name__iregex='^' + Alias.normalize(pattern))
            )

        only_active = "only_active" not in self.request.GET or self.request.GET["only_active"] != '0'

        if only_active:
            qs = qs.filter(date_start__lte=timezone.now().today(), date_end__gte=timezone.now().today())

        if "roles" in self.request.GET:
            roles_str = self.request.GET["roles"].replace(' ', '').split(',') if self.request.GET["roles"] else ['0']
            roles_int = map(int, roles_str)
            qs = qs.filter(roles__in=roles_int)

        qs = qs.order_by('-date_start', 'user__username')

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.filter(
            PermissionBackend.filter_queryset(self.request, Club, "view")
        ).get(pk=self.kwargs["pk"])
        context["club"] = club

        applicable_roles = Role.objects.filter(Q(weirole__isnull=not hasattr(club, 'weiclub'))
                                               & (Q(for_club__isnull=True) | Q(for_club=club))).all()
        context["applicable_roles"] = applicable_roles

        context["only_active"] = "only_active" not in self.request.GET or self.request.GET["only_active"] != '0'

        return context
