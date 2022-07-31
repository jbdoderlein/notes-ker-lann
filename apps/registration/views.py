# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import resolve_url, redirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView
from django.views.generic.edit import FormMixin
from django_tables2 import SingleTableView
from member.forms import ProfileForm
from member.models import Membership, Club
from note.models import SpecialTransaction, Alias
from note.templatetags.pretty_money import pretty_money
from permission.backends import PermissionBackend
from permission.models import Role
from permission.views import ProtectQuerysetMixin

from .forms import SignUpForm, ValidationForm
from .tables import FutureUserTable
from .tokens import email_validation_token


class UserCreateView(CreateView):
    """
    A view to create a User and add a Profile
    """

    form_class = SignUpForm
    template_name = 'registration/signup.html'
    second_form = ProfileForm
    extra_context = {"title": _("Register new user")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = self.second_form(self.request.POST if self.request.POST else None)
        del context["profile_form"].fields["section"]
        del context["profile_form"].fields["report_frequency"]
        del context["profile_form"].fields["last_report"]

        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        If the form is valid, then the user is created with is_active set to False
        so that the user cannot log in until the email has been validated.
        The user must also wait that someone validate her/his account.
        """
        profile_form = ProfileForm(data=self.request.POST)
        if not profile_form.is_valid():
            return self.form_invalid(form)

        # Save the user and the profile
        user = form.save(commit=False)
        user.is_active = False
        profile_form.instance.user = user
        profile = profile_form.save(commit=False)
        user.profile = profile
        user._force_save = True
        user.save()
        user.refresh_from_db()
        profile.user = user
        profile._force_save = True
        profile.save()

        user.profile.send_email_validation_link()

        return super().form_valid(form)

    def get_success_url(self):
        # Direct access to validation menu if we have the right to validate it
        if PermissionBackend.check_perm(self.request, 'auth.view_user', self.object):
            return reverse_lazy('registration:future_user_detail', args=(self.object.pk,))
        return reverse_lazy('registration:email_validation_sent')


class UserValidateView(TemplateView):
    """
    A view to validate the email address.
    """
    title = _("Email validation")
    template_name = 'registration/email_validation_complete.html'
    extra_context = {"title": _("Validate email")}

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
            # The user must wait that someone validates the account before the user can be active and login.
            self.validlink = True
            user.is_active = user.profile.registration_valid or user.is_superuser
            user.profile.email_confirmed = True
            user._force_save = True
            user.save()
            user.profile._force_save = True
            user.profile.save()
        return self.render_to_response(self.get_context_data(), status=200 if self.validlink else 400)

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
    extra_context = {"title": _('Email validation email sent')}


class UserResendValidationEmailView(LoginRequiredMixin, ProtectQuerysetMixin, DetailView):
    """
    Rensend the email validation link.
    """
    model = User
    extra_context = {"title": _("Resend email validation link")}

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
    extra_context = {"title": _("Pre-registered users list")}

    def get_queryset(self, **kwargs):
        """
        Filter the table with the given parameter.
        :param kwargs:
        :return:
        """
        qs = super().get_queryset().distinct().filter(profile__registration_valid=False)
        if "search" in self.request.GET and self.request.GET["search"]:
            pattern = self.request.GET["search"]

            qs = qs.filter(
                Q(first_name__iregex=pattern)
                | Q(last_name__iregex=pattern)
                | Q(profile__section__iregex=pattern)
                | Q(username__iregex="^" + pattern)
            )

        return qs

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
    extra_context = {"title": _("Registration detail")}

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.object = self.get_object()
        return self.form_valid(form) if form.is_valid() else self.form_invalid(form)

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

    @transaction.atomic
    def form_valid(self, form):
        """
        Finally validate the registration, with creating the membership.
        """
        user = self.get_object()

        if Alias.objects.filter(normalized_name=Alias.normalize(user.username)).exists():
            # Don't try to hack an existing account.
            form.add_error(None, _("An alias with a similar name already exists."))
            return self.form_invalid(form)

        # Get form data
        credit_type = form.cleaned_data["credit_type"]
        credit_amount = form.cleaned_data["credit_amount"]
        last_name = form.cleaned_data["last_name"]
        first_name = form.cleaned_data["first_name"]
        bank = form.cleaned_data["bank"]
        join_bde = form.cleaned_data["join_bde"]
        join_kfet = form.cleaned_data["join_kfet"]


        if not join_bde:
            # This software belongs to the BDE.
            form.add_error('join_bde', _("You must join the BDE."))
            return super().form_invalid(form)

        # Calculate required registration fee
        fee = 0
        bde = Club.objects.get(name="BDE")
        bde_fee = bde.membership_fee_paid if user.profile.paid else bde.membership_fee_unpaid
        # This is mandatory.
        fee += bde_fee if join_bde else 0
        kfet = Club.objects.get(name="Kfet")
        kfet_fee = kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid
        # Add extra fee for the full membership
        fee += kfet_fee if join_kfet else 0

        # If the bank pays, then we don't credit now. Treasurers will validate the transaction
        # and credit the note later.
        credit_type = credit_type

        # If the user does not select any payment method, then no credit will be performed.
        credit_amount = 0 if credit_type is None else credit_amount

        if fee > credit_amount:
            # Check if the user credits enough money
            form.add_error('credit_type',
                           _("The entered amount is not enough for the memberships, should be at least {}")
                           .format(pretty_money(fee)))
            return self.form_invalid(form)

        # Check that payment information are filled, like last name and first name
        if credit_type is not None and credit_amount > 0 and not SpecialTransaction.validate_payment_form(form):
            return self.form_invalid(form)

        # Save the user and finally validate the registration
        # Saving the user creates the associated note
        ret = super().form_valid(form)
        user.is_active = user.profile.email_confirmed or user.is_superuser
        user.profile.registration_valid = True
        user.save()
        user.profile.save()
        user.refresh_from_db()

        if credit_type is not None and credit_amount > 0:
            # Credit the note
            SpecialTransaction.objects.create(
                source=credit_type,
                destination=user.note,
                quantity=1,
                amount=credit_amount,
                reason="Crédit " +  credit_type.special_type + " (Inscription)",
                last_name=last_name,
                first_name=first_name,
                bank=bank,
                valid=True,
            )

        if join_bde:
            # Create membership for the user to the BDE starting today
            membership = Membership(
                club=bde,
                user=user,
                fee=bde_fee,
            )
            membership.save()
            membership.refresh_from_db()
            membership.roles.add(Role.objects.get(name="Adhérent BDE"))
            membership.save()

        if join_kfet:
            # Create membership for the user to the Kfet starting today
            membership = Membership(
                club=kfet,
                user=user,
                fee=kfet_fee,
            )
            
            membership.save()
            membership.refresh_from_db()
            membership.roles.add(Role.objects.get(name="Adhérent Kfet"))
            membership.save()

        
        return ret

    def get_success_url(self):
        return reverse_lazy('member:user_detail', args=(self.get_object().pk, ))


class FutureUserInvalidateView(ProtectQuerysetMixin, LoginRequiredMixin, View):
    """
    Delete a pre-registered user.
    """
    extra_context = {"title": _("Invalidate pre-registration")}

    def get(self, request, *args, **kwargs):
        """
        Delete the pre-registered user which id is given in the URL.
        """
        user = User.objects.filter(profile__registration_valid=False)\
            .filter(PermissionBackend.filter_queryset(request, User, "change", "is_valid"))\
            .get(pk=self.kwargs["pk"])
        

        user.delete()

        return redirect('registration:future_user_list')
