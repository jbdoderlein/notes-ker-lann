# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import io
from datetime import datetime, timedelta

from PIL import Image
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import HiddenInput
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin
from django_tables2.views import SingleTableView
from rest_framework.authtoken.models import Token
from note.forms import ImageForm
from note.models import Alias, NoteUser
from note.models.transactions import Transaction
from note.tables import HistoryTable, AliasTable
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import SignUpForm, ProfileForm, ClubForm, MembershipForm, CustomAuthenticationForm
from .models import Club, Membership
from .tables import ClubTable, UserTable, MembershipTable


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        self.request.session['permission_mask'] = form.cleaned_data['permission_mask'].rank
        return super().form_valid(form)


class UserCreateView(CreateView):
    """
    Une vue pour inscrire un utilisateur et lui créer un profile
    """

    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'member/signup.html'
    second_form = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = self.second_form()

        return context

    def form_valid(self, form):
        profile_form = ProfileForm(self.request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.profile = profile_form.save(commit=False)
            user.save()
            user.profile.save()
        return super().form_valid(form)


class UserUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'member/profile_update.html'
    context_object_name = 'user_object'
    profile_form = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = self.profile_form(instance=context['user_object'].profile)
        context['title'] = _("Update Profile")
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'username' not in form.data:
            return form
        new_username = form.data['username']
        # Si l'utilisateur cherche à modifier son pseudo, le nouveau pseudo ne doit pas être proche d'un alias existant
        note = NoteUser.objects.filter(
            alias__normalized_name=Alias.normalize(new_username))
        if note.exists() and note.get().user != self.object:
            form.add_error('username',
                           _("An alias with a similar name already exists."))
        return form

    def form_valid(self, form):
        profile_form = ProfileForm(
            data=self.request.POST,
            instance=self.object.profile,
        )
        if form.is_valid() and profile_form.is_valid():
            new_username = form.data['username']
            alias = Alias.objects.filter(name=new_username)
            # Si le nouveau pseudo n'est pas un de nos alias,
            # on supprime éventuellement un alias similaire pour le remplacer
            if not alias.exists():
                similar = Alias.objects.filter(
                    normalized_name=Alias.normalize(new_username))
                if similar.exists():
                    similar.delete()

            user = form.save(commit=False)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            user.save()
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        if kwargs:
            return reverse_lazy('member:user_detail',
                                kwargs={'pk': kwargs['id']})
        else:
            return reverse_lazy('member:user_detail', args=(self.object.id,))


class UserDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Affiche les informations sur un utilisateur, sa note, ses clubs...
    """
    model = User
    context_object_name = "user_object"
    template_name = "member/profile_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context['user_object']
        history_list = \
            Transaction.objects.all().filter(Q(source=user.note) | Q(destination=user.note)).order_by("-id")\
            .filter(PermissionBackend.filter_queryset(self.request.user, Transaction, "view"))
        context['history_list'] = HistoryTable(history_list)
        club_list = Membership.objects.filter(user=user, date_end__gte=datetime.today())\
            .filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view"))
        context['club_list'] = MembershipTable(data=club_list)
        return context


class UserListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    Affiche la liste des utilisateurs, avec une fonction de recherche statique
    """
    model = User
    table_class = UserTable
    template_name = 'member/user_list.html'

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        if "search" in self.request.GET:
            pattern = self.request.GET["search"]

            if not pattern:
                return qs.none()

            qs = qs.filter(
                Q(first_name__iregex=pattern)
                | Q(last_name__iregex=pattern)
                | Q(profile__section__iregex=pattern)
                | Q(note__alias__name__iregex="^" + pattern)
                | Q(note__alias__normalized_name__iregex=Alias.normalize("^" + pattern))
            )
        else:
            qs = qs.none()

        return qs[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = _("Search user")

        return context


class ProfileAliasView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    model = User
    template_name = 'member/profile_alias.html'
    context_object_name = 'user_object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = context['object'].note
        context["aliases"] = AliasTable(note.alias_set.all())
        return context


class PictureUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, FormMixin, DetailView):
    form_class = ImageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.POST, self.request.FILES)
        return context

    def get_success_url(self):
        return reverse_lazy('member:user_detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.object = self.get_object()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print('is_invalid')
            print(form)
            return self.form_invalid(form)

    def form_valid(self, form):
        image_field = form.cleaned_data['image']
        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        w = form.cleaned_data['width']
        h = form.cleaned_data['height']
        # image crop and resize
        image_file = io.BytesIO(image_field.read())
        # ext = image_field.name.split('.')[-1].lower()
        # TODO: support GIF format
        image = Image.open(image_file)
        image = image.crop((x, y, x + w, y + h))
        image_clean = image.resize((settings.PIC_WIDTH,
                                    settings.PIC_RATIO * settings.PIC_WIDTH),
                                   Image.ANTIALIAS)
        image_file = io.BytesIO()
        image_clean.save(image_file, "PNG")
        image_field.file = image_file
        # renaming
        filename = "{}_pic.png".format(self.object.note.pk)
        image_field.name = filename
        self.object.note.display_image = image_field
        self.object.note.save()
        return super().form_valid(form)


class ProfilePictureUpdateView(PictureUpdateView):
    model = User
    template_name = 'member/profile_picture_update.html'
    context_object_name = 'user_object'


class ManageAuthTokens(LoginRequiredMixin, TemplateView):
    """
    Affiche le jeton d'authentification, et permet de le regénérer
    """
    model = Token
    template_name = "member/manage_auth_tokens.html"

    def get(self, request, *args, **kwargs):
        if 'regenerate' in request.GET and Token.objects.filter(user=request.user).exists():
            Token.objects.get(user=self.request.user).delete()
            return redirect(reverse_lazy('member:auth_token') + "?show",
                            permanent=True)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = Token.objects.get_or_create(user=self.request.user)[0]
        return context


# ******************************* #
#              CLUB               #
# ******************************* #


class ClubCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Club
    """
    model = Club
    form_class = ClubForm
    success_url = reverse_lazy('member:club_list')

    def form_valid(self, form):
        return super().form_valid(form)


class ClubListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing Clubs
    """
    model = Club
    table_class = ClubTable


class ClubDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    model = Club
    context_object_name = "club"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        club = context["club"]
        if PermissionBackend.check_perm(self.request.user, "member.change_club_membership_start", club):
            club.update_membership_dates()

        club_transactions = Transaction.objects.all().filter(Q(source=club.note) | Q(destination=club.note))\
            .filter(PermissionBackend.filter_queryset(self.request.user, Transaction, "view")).order_by('-id')
        context['history_list'] = HistoryTable(club_transactions)
        club_member = Membership.objects.filter(
            club=club,
            date_end__gte=datetime.today(),
        ).filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view"))

        context['member_list'] = MembershipTable(data=club_member)

        empty_membership = Membership(
            club=club,
            user=User.objects.first(),
            date_start=datetime.now().date(),
            date_end=datetime.now().date(),
            fee=0,
        )
        context["can_add_members"] = PermissionBackend()\
            .has_perm(self.request.user, "member.add_membership", empty_membership)

        return context


class ClubAliasView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    model = Club
    template_name = 'member/club_alias.html'
    context_object_name = 'club'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = context['object'].note
        context["aliases"] = AliasTable(note.alias_set.all())
        return context


class ClubUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    model = Club
    context_object_name = "club"
    form_class = ClubForm
    template_name = "member/club_form.html"

    def get_success_url(self):
        return reverse_lazy("member:club_detail", kwargs={"pk": self.object.pk})


class ClubPictureUpdateView(PictureUpdateView):
    model = Club
    template_name = 'member/club_picture_update.html'
    context_object_name = 'club'

    def get_success_url(self):
        return reverse_lazy('member:club_detail', kwargs={'pk': self.object.id})


class ClubAddMemberView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'member/add_members.html'

    def get_context_data(self, **kwargs):
        club = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view"))\
            .get(pk=self.kwargs["pk"])
        context = super().get_context_data(**kwargs)
        context['club'] = club

        return context

    def form_valid(self, form):
        club = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view"))\
            .get(pk=self.kwargs["pk"])
        user = self.request.user
        form.instance.club = club

        if user.profile.paid:
            fee = club.membership_fee_paid
        else:
            fee = club.membership_fee_unpaid
        if user.note.balance < fee and not Membership.objects.filter(
                club__name="Kfet",
                user=user,
                date_start__lte=datetime.now().date(),
                date_end__gte=datetime.now().date(),
        ).exists():
            # Users without a valid Kfet membership can't have a negative balance.
            # Club 2 = Kfet (hard-code :'( )
            # TODO Send a notification to the user (with a mail?) to tell her/him to credit her/his note
            form.add_error('user',
                           _("This user don't have enough money to join this club, and can't have a negative balance."))

        if club.parent_club is not None:
            if not Membership.objects.filter(user=form.instance.user, club=club.parent_club).exists():
                form.add_error('user', _('User is not a member of the parent club') + ' ' + club.parent_club.name)
                return super().form_invalid(form)

        if Membership.objects.filter(
                user=form.instance.user,
                club=club,
                date_start__lte=form.instance.date_start,
                date_end__gte=form.instance.date_start,
        ).exists():
            form.add_error('user', _('User is already a member of the club'))
            return super().form_invalid(form)

        if form.instance.club.membership_start and form.instance.date_start < form.instance.club.membership_start:
            form.add_error('user', _("The membership must start after {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_start))
            return super().form_invalid(form)

        if form.instance.club.membership_end and form.instance.date_start > form.instance.club.membership_end:
            form.add_error('user', _("The membership must begin before {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_start))
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('member:club_detail', kwargs={'pk': self.object.club.id})


class ClubManageRolesView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'member/add_members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = self.object.club
        context['club'] = club
        form = context['form']
        form.fields['user'].disabled = True
        form.fields['date_start'].widget = HiddenInput()

        return context

    def form_valid(self, form):
        if form.instance.club.membership_start and form.instance.date_start < form.instance.club.membership_start:
            form.add_error('user', _("The membership must start after {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_start))
            return super().form_invalid(form)

        if form.instance.club.membership_end and form.instance.date_start > form.instance.club.membership_end:
            form.add_error('user', _("The membership must begin before {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_start))
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('member:club_detail', kwargs={'pk': self.object.club.id})


class ClubRenewMembershipView(ProtectQuerysetMixin, LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        user = self.request.user
        membership = Membership.objects.filter(PermissionBackend.filter_queryset(user, Membership, "change"))\
            .filter(pk=self.kwargs["pk"]).get()

        if Membership.objects.filter(
            club=membership.club,
            user=membership.user,
            date_start__gte=membership.club.membership_start,
            date_end__lte=membership.club.membership_end,
        ).exists():
            raise ValidationError(_("This membership is already renewed"))

        new_membership = Membership.objects.create(
            user=user,
            club=membership.club,
            date_start=membership.date_end + timedelta(days=1),
        )
        new_membership.roles.set(membership.roles.all())
        new_membership.save()

        return redirect(reverse_lazy('member:club_detail', kwargs={'pk': membership.club.pk}))
