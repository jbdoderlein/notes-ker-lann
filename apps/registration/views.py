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
from django.views.generic import CreateView, TemplateView, DetailView
from django_tables2 import SingleTableView
from member.forms import ProfileForm
from member.models import Profile
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import SignUpForm
from .tables import FutureUserTable
from .tokens import account_activation_token


class UserCreateView(CreateView):
    """
    Une vue pour inscrire un utilisateur et lui créer un profil
    """

    form_class = SignUpForm
    success_url = reverse_lazy('registration:account_activation_sent')
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


class UserActivateView(TemplateView):
    title = _("Account Activation")
    template_name = 'registration/account_activation_complete.html'

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

        if user is not None and account_activation_token.check_token(user, token):
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


class UserActivationEmailSentView(TemplateView):
    template_name = 'registration/account_activation_email_sent.html'
    title = _('Account activation email sent')


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


class FutureUserDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Affiche les informations sur un utilisateur, sa note, ses clubs...
    """
    model = User
    context_object_name = "user_object"
    template_name = "registration/future_profile_detail.html"

    def get_queryset(self, **kwargs):
        """
        We only display information of a not registered user.
        """
        return super().get_queryset().filter(profile__registration_valid=False)


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
