# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q, BooleanField
from django.shortcuts import resolve_url, redirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView
from django.views.generic.edit import FormMixin
from django_tables2 import SingleTableView
from member.forms import ProfileForm
from member.models import Membership, Club, Role
from note.models import SpecialTransaction, NoteSpecial
from note.templatetags.pretty_money import pretty_money
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin
from wei.models import WEIClub

from .forms import SignUpForm, ValidationForm, WEISignupForm
from .tables import FutureUserTable
from .tokens import email_validation_token


class UserCreateView(CreateView):
    """
    Une vue pour inscrire un utilisateur et lui créer un profil
    """

    form_class = SignUpForm
    success_url = reverse_lazy('registration:email_validation_sent')
    template_name = 'registration/signup.html'
    second_form = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = self.second_form()

        if "wei" in settings.INSTALLED_APPS:
            from wei.forms import WEIRegistrationForm
            wei_form = WEIRegistrationForm()
            del wei_form.fields["user"]
            del wei_form.fields["caution_check"]
            context["wei_form"] = wei_form
            context["wei_registration_form"] = WEISignupForm()

        return context

    def form_valid(self, form):
        """
        If the form is valid, then the user is created with is_active set to False
        so that the user cannot log in until the email has been validated.
        The user must also wait that someone validate her/his account.
        """
        profile_form = ProfileForm(data=self.request.POST)
        if not profile_form.is_valid():
            return self.form_invalid(form)

        wei_form = None

        if "wei" in settings.INSTALLED_APPS:
            wei_signup_form = WEISignupForm(self.request.POST)
            if wei_signup_form.is_valid() and wei_signup_form.cleaned_data["wei_registration"]:
                from wei.forms import WEIRegistrationForm
                wei_form = WEIRegistrationForm(self.request.POST)
                del wei_form.fields["user"]
                del wei_form.fields["caution_check"]

                if not wei_form.is_valid():
                    return self.form_invalid(wei_form)

        # Save the user and the profile
        user = form.save(commit=False)
        user.is_active = False
        profile_form.instance.user = user
        profile = profile_form.save(commit=False)
        user.profile = profile
        user.save()
        user.refresh_from_db()
        profile.user = user
        profile.save()

        user.profile.send_email_validation_link()

        if wei_form is not None:
            wei_registration = wei_form.instance
            wei_registration.user = user
            wei_registration.wei = WEIClub.objects.order_by('date_start').last()
            wei_registration.caution_check = False
            wei_registration.save()

        return super().form_valid(form)


class UserValidateView(TemplateView):
    """
    A view to validate the email address.
    """
    title = _("Email validation")
    template_name = 'registration/email_validation_complete.html'

    def get(self, *args, **kwargs):
        """
        With a given token and user id (in params), validate the email address.
        """
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        user = self.get_user(kwargs['uidb64'])
        token = kwargs['token']

        # Validate the token
        if user is not None and email_validation_token.check_token(user, token):
            self.validlink = True
            # The user must wait that someone validates the account before the user can be active and login.
            user.is_active = user.profile.registration_valid or user.is_superuser
            user.profile.email_confirmed = True
            user.save()
            user.profile.save()
            return super().dispatch(*args, **kwargs)
        else:
            # Display the "Email validation unsuccessful" page.
            return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        """
        Get user from the base64-encoded string.
        """
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_object'] = self.get_user(self.kwargs["uidb64"])
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'title': _('Email validation unsuccessful'),
                'validlink': False,
            })
        return context


class UserValidationEmailSentView(TemplateView):
    """
    Display the information that the validation link has been sent.
    """
    template_name = 'registration/email_validation_email_sent.html'
    title = _('Email validation email sent')


class UserResendValidationEmailView(LoginRequiredMixin, ProtectQuerysetMixin, DetailView):
    """
    Rensend the email validation link.
    """
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        user.profile.send_email_validation_link()

        url = 'member:user_detail' if user.profile.registration_valid else 'registration:future_user_detail'
        return redirect(url, user.id)


class FutureUserListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    Display pre-registered users, with a search bar
    """
    model = User
    table_class = FutureUserTable
    template_name = 'registration/future_user_list.html'

    def get_queryset(self, **kwargs):
        """
        Filter the table with the given parameter.
        :param kwargs:
        :return:
        """
        qs = super().get_queryset().filter(profile__registration_valid=False)
        if "search" in self.request.GET:
            pattern = self.request.GET["search"]

            if not pattern:
                return qs.none()

            qs = qs.filter(
                Q(first_name__iregex=pattern)
                | Q(last_name__iregex=pattern)
                | Q(profile__section__iregex=pattern)
                | Q(username__iregex="^" + pattern)
            )
        else:
            qs = qs.none()

        return qs[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = _("Unregistered users")

        return context


class FutureUserDetailView(ProtectQuerysetMixin, LoginRequiredMixin, FormMixin, DetailView):
    """
    Display information about a pre-registered user, in order to complete the registration.
    """
    model = User
    form_class = ValidationForm
    context_object_name = "user_object"
    template_name = "registration/future_profile_detail.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.object = self.get_object()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_queryset(self, **kwargs):
        """
        We only display information of a not registered user.
        """
        return super().get_queryset().filter(profile__registration_valid=False)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user = self.get_object()
        fee = 0
        bde = Club.objects.get(name="BDE")
        fee += bde.membership_fee_paid if user.profile.paid else bde.membership_fee_unpaid
        kfet = Club.objects.get(name="Kfet")
        fee += kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid
        ctx["total_fee"] = "{:.02f}".format(fee / 100, )

        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.get_object()
        form.fields["last_name"].initial = user.last_name
        form.fields["first_name"].initial = user.first_name
        return form

    def form_valid(self, form):
        user = self.get_object()

        # Get form data
        soge = form.cleaned_data["soge"]
        credit_type = form.cleaned_data["credit_type"]
        credit_amount = form.cleaned_data["credit_amount"]
        last_name = form.cleaned_data["last_name"]
        first_name = form.cleaned_data["first_name"]
        bank = form.cleaned_data["bank"]
        join_BDE = form.cleaned_data["join_BDE"]
        join_Kfet = form.cleaned_data["join_Kfet"]

        if soge:
            # If Société Générale pays the inscription, the user joins the two clubs
            join_BDE = True
            join_Kfet = True

        if not join_BDE:
            form.add_error('join_BDE', _("You must join the BDE."))
            return super().form_invalid(form)

        fee = 0
        bde = Club.objects.get(name="BDE")
        bde_fee = bde.membership_fee_paid if user.profile.paid else bde.membership_fee_unpaid
        if join_BDE:
            fee += bde_fee
        kfet = Club.objects.get(name="Kfet")
        kfet_fee = kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid
        if join_Kfet:
            fee += kfet_fee

        if soge:
            # Fill payment information if Société Générale pays the inscription
            credit_type = NoteSpecial.objects.get(special_type="Virement bancaire")
            credit_amount = fee
            bank = "Société générale"

        print("OK")

        if join_Kfet and not join_BDE:
            form.add_error('join_Kfet', _("You must join BDE club before joining Kfet club."))

        if fee > credit_amount:
            # Check if the user credits enough money
            form.add_error('credit_type',
                           _("The entered amount is not enough for the memberships, should be at least {}")
                           .format(pretty_money(fee)))
            return self.form_invalid(form)

        if credit_type is not None and credit_amount > 0:
            if not last_name or not first_name or (not bank and credit_type.special_type == "Chèque"):
                if not last_name:
                    form.add_error('last_name', _("This field is required."))
                if not first_name:
                    form.add_error('first_name', _("This field is required."))
                if not bank and credit_type.special_type == "Chèque":
                    form.add_error('bank', _("This field is required."))
                return self.form_invalid(form)

        # Save the user and finally validate the registration
        # Saving the user creates the associated note
        ret = super().form_valid(form)
        user.is_active = user.profile.email_confirmed or user.is_superuser
        user.profile.registration_valid = True
        # Store if Société générale paid for next years
        user.profile.soge = soge
        user.save()
        user.profile.save()

        if credit_type is not None and credit_amount > 0:
            # Credit the note
            SpecialTransaction.objects.create(
                source=credit_type,
                destination=user.note,
                quantity=1,
                amount=credit_amount,
                reason="Crédit " + ("Société générale" if soge else credit_type.special_type) + " (Inscription)",
                last_name=last_name,
                first_name=first_name,
                bank=bank,
                valid=True,
            )

        if join_BDE:
            # Create membership for the user to the BDE starting today
            membership = Membership.objects.create(
                club=bde,
                user=user,
                fee=bde_fee,
            )
            membership.roles.add(Role.objects.get(name="Adhérent BDE"))
            membership.save()

        if join_Kfet:
            # Create membership for the user to the Kfet starting today
            membership = Membership.objects.create(
                club=kfet,
                user=user,
                fee=kfet_fee,
            )
            membership.roles.add(Role.objects.get(name="Adhérent Kfet"))
            membership.save()

        return ret

    def get_success_url(self):
        return reverse_lazy('member:user_detail', args=(self.get_object().pk, ))


class FutureUserInvalidateView(ProtectQuerysetMixin, LoginRequiredMixin, View):
    """
    Delete a pre-registered user.
    """

    def get(self, request, *args, **kwargs):
        """
        Delete the pre-registered user which id is given in the URL.
        """
        user = User.objects.filter(profile__registration_valid=False)\
            .filter(PermissionBackend.filter_queryset(request.user, User, "change", "is_valid"))\
            .get(pk=self.kwargs["pk"])

        user.delete()

        return redirect('registration:future_user_list')
