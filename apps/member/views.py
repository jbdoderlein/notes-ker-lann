# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import io

from PIL import Image
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.views.generic.edit import FormMixin
from django_tables2.views import SingleTableView
from rest_framework.authtoken.models import Token
from note.forms import ImageForm
from note.models import Alias, NoteUser
from note.models.notes import NoteActivity
from note.models.transactions import Transaction
from note.tables import HistoryTable, AliasTable, NoteActivityTable
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .filters import UserFilter, UserFilterFormHelper
from .forms import SignUpForm, ProfileForm, ClubForm, MembershipForm, MemberFormSet, FormSetHelper, \
    CustomAuthenticationForm, NoteActivityForm
from .models import Club, Membership
from .tables import ClubTable, UserTable


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
        club_list = Membership.objects.all().filter(user=user)\
            .filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view")).only("club")
        context['club_list'] = ClubTable(club_list)
        return context


class UserListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    Affiche la liste des utilisateurs, avec une fonction de recherche statique
    """
    model = User
    table_class = UserTable
    template_name = 'member/user_list.html'
    filter_class = UserFilter
    formhelper_class = UserFilterFormHelper

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
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
        club_transactions = Transaction.objects.all().filter(Q(source=club.note) | Q(destination=club.note))\
            .filter(PermissionBackend.filter_queryset(self.request.user, Transaction, "view")).order_by('-id')
        context['history_list'] = HistoryTable(club_transactions)
        club_member = Membership.objects.filter(club=club)\
            .filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view")).all()
        # TODO: consider only valid Membership
        context['member_list'] = club_member
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

    def get_queryset(self, **kwargs):
        return super().get_queryset().filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view")
                                             | PermissionBackend.filter_queryset(self.request.user, Membership,
                                                                                 "change"))

    def get_context_data(self, **kwargs):
        club = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view"))\
            .get(pk=self.kwargs["pk"])
        context = super().get_context_data(**kwargs)
        context['formset'] = MemberFormSet()
        context['helper'] = FormSetHelper()
        context['club'] = club
        context['no_cache'] = True

        return context

    def post(self, request, *args, **kwargs):
        return
        # TODO: Implement POST
        # formset = MembershipFormset(request.POST)
        # if formset.is_valid():
        #     return self.form_valid(formset)
        # else:
        #     return self.form_invalid(formset)

    def form_valid(self, formset):
        formset.save()
        return super().form_valid(formset)


class ClubLinkedNotesView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    model = NoteActivity
    table_class = NoteActivityTable

    def get_queryset(self):
        return super().get_queryset().filter(club=self.get_object())

    def get_object(self):
        if hasattr(self, 'object'):
            return self.object
        self.object = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view"))\
            .get(pk=int(self.kwargs["pk"]))
        return self.object

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        club = ctx["object"] = ctx["club"] = self.get_object()

        empty_note = NoteActivity(note_name="", club=club, controller=self.request.user)
        ctx["can_create"] = PermissionBackend().has_perm(self.request.user, "note.add_noteactivity", empty_note)

        return ctx


class ClubLinkedNoteCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    model = NoteActivity
    form_class = NoteActivityForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        club = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view"))\
            .get(pk=self.kwargs["club_pk"])
        ctx["object"] = ctx["club"] = club
        ctx["form"].fields["club"].initial = club

        return ctx

    def get_success_url(self):
        self.object.refresh_from_db()
        return reverse_lazy('member:club_linked_note_detail',
                            kwargs={"club_pk": self.object.club.pk, "pk": self.object.pk})


class ClubLinkedNoteUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    model = NoteActivity
    form_class = NoteActivityForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["club"] = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view"))\
            .get(pk=self.kwargs["club_pk"])

        return ctx

    def get_success_url(self):
        return reverse_lazy('member:club_linked_note_detail',
                            kwargs={"club_pk": self.object.club.pk, "pk": self.object.pk})


class ClubLinkedNoteDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    model = NoteActivity

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        note = self.get_queryset().filter(pk=self.kwargs["pk"]).get()

        transactions = Transaction.objects.filter(Q(source=note) | Q(destination=note))\
            .filter(PermissionBackend.filter_queryset(self.request.user, Transaction, "view")).order_by("-id")
        ctx['history_list'] = HistoryTable(transactions)
        ctx["note"] = note
        ctx["club"] = note.club

        return ctx
