# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import resolve_url, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, TemplateView, DetailView, FormView
from django_tables2 import SingleTableView
from member.forms import ProfileForm
from member.models import Membership, Club
from note.models import SpecialTransaction, Transaction
from note.templatetags.pretty_money import pretty_money
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import SignUpForm, ValidationForm
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

        return context

    def form_valid(self, form):
        """
        If the form is valid, then the user is created with is_active set to False
        so that the user cannot log in until the email has been validated.
        """
        profile_form = ProfileForm(data=self.request.POST)
        if not profile_form.is_valid():
            return self.form_invalid(form)

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

        return super().form_valid(form)


class UserValidateView(LoginRequiredMixin, ProtectQuerysetMixin, TemplateView):
    title = _("Account Activation")
    template_name = 'registration/email_validation_complete.html'

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        """
        The dispatch method looks at the request to determine whether it is a GET, POST, etc,
        and relays the request to a matching method if one is defined, or raises HttpResponseNotAllowed
        if not. We chose to check the token in the dispatch method to mimic PasswordReset from
        django.contrib.auth
        """
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        user = self.get_user(kwargs['uidb64'])
        token = kwargs['token']

        if user is not None and email_validation_token.check_token(user, token):
            self.validlink = True
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            return super().dispatch(*args, **kwargs)
        else:
            # Display the "Account Activation unsuccessful" page.
            return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'title': _('Account Activation unsuccessful'),
                'validlink': False,
            })
        return context


class UserValidationEmailSentView(LoginRequiredMixin, ProtectQuerysetMixin, TemplateView):
    template_name = 'registration/email_validation_email_sent.html'
    title = _('Account activation email sent')


class UserResendValidationEmailView(LoginRequiredMixin, ProtectQuerysetMixin, DetailView):
    model = User

    def get_queryset(self, **kwargs):
        return super().get_queryset(**kwargs).filter(profile__email_confirmed=False)

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        user.profile.send_email_validation_link()

        url = 'member:user_detail' if user.profile.registration_valid else 'registration:future_user_detail'
        return redirect(url, user.id)


class FutureUserListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    Affiche la liste des utilisateurs, avec une fonction de recherche statique
    """
    model = User
    table_class = FutureUserTable
    template_name = 'registration/future_user_list.html'

    def get_queryset(self, **kwargs):
        return super().get_queryset().filter(profile__registration_valid=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = _("Unregistered users")

        return context


class FutureUserDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView, FormView):
    """
    Affiche les informations sur un utilisateur, sa note, ses clubs...
    """
    model = User
    form_class = ValidationForm
    context_object_name = "user_object"
    template_name = "registration/future_profile_detail.html"

    def get_queryset(self, **kwargs):
        """
        We only display information of a not registered user.
        """
        return super().get_queryset().filter(profile__registration_valid=False)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.get_object()
        form.fields["last_name"].initial = user.last_name
        form.fields["first_name"].initial = user.first_name
        return form

    def form_valid(self, form):
        user = self.object = self.get_object()

        print(form.cleaned_data)
        credit_type = form.cleaned_data["credit_type"]
        credit_amount = form.cleaned_data["credit_amount"]
        last_name = form.cleaned_data["last_name"]
        first_name = form.cleaned_data["first_name"]
        bank = form.cleaned_data["bank"]
        join_BDE = form.cleaned_data["join_BDE"]
        join_Kfet = form.cleaned_data["join_Kfet"]

        fee = 0
        bde = Club.objects.get(name="BDE")
        bde_fee = bde.membership_fee_paid if user.profile.paid else bde.membership_fee_unpaid
        if join_BDE:
            fee += bde_fee
        kfet = Club.objects.get(name="Kfet")
        kfet_fee = kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid
        if join_Kfet:
            fee += kfet_fee

        if join_Kfet and not join_BDE:
            form.add_error('join_Kfet', _("You must join BDE club before joining Kfet club."))

        if fee > credit_amount:
            form.add_error('credit_type',
                           _("The entered amount is not enough for the memberships, should be at least {}")
                           .format(pretty_money(fee)))
            return self.form_invalid(form)

        if credit_type is not None and credit_amount > 0:
            if not last_name or not first_name or not bank:
                if not last_name:
                    form.add_error('last_name', _("This field is required."))
                if not first_name:
                    form.add_error('first_name', _("This field is required."))
                if not bank:
                    form.add_error('bank', _("This field is required."))
                return self.form_invalid(form)

        ret = super().form_valid(form)
        user.is_active = True
        user.profile.registration_valid = True
        user.save()
        user.profile.save()

        if credit_type is not None and credit_amount > 0:
            SpecialTransaction.objects.create(
                source=credit_type,
                destination=user.note,
                quantity=1,
                amount=credit_amount,
                reason="Crédit " + credit_type.special_type + " (Inscription)",
                last_name=last_name,
                first_name=first_name,
                bank=bank,
                valid=True,
            )

        if join_BDE:
            Membership.objects.create(
                club=bde,
                user=user,
                fee=bde_fee,
            )

        if join_Kfet:
            Membership.objects.create(
                club=kfet,
                user=user,
                fee=kfet_fee,
            )

        return ret

    def get_success_url(self):
        return reverse_lazy('member:user_detail', args=(self.get_object().pk, ))


class FutureUserInvalidateView(ProtectQuerysetMixin, LoginRequiredMixin, View):
    """
    Affiche les informations sur un utilisateur, sa note, ses clubs...
    """

    def dispatch(self, request, *args, **kwargs):
        user = User.objects.filter(profile__registration_valid=False)\
            .filter(PermissionBackend.filter_queryset(request.user, User, "change", "is_valid"))\
            .get(pk=self.kwargs["pk"])

        user.delete()

        return redirect('registration:future_user_list')
