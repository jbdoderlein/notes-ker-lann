# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView,DeleteView
from django.views.generic.edit import FormMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.exceptions import ValidationError

from django_tables2.views import SingleTableView
from rest_framework.authtoken.models import Token
from dal import autocomplete
from PIL import Image

from note.models import Alias, NoteUser
from note.models.transactions import Transaction
from note.tables import HistoryTable, AliasTable
from note.forms import AliasForm, ImageForm

from .models import Profile, Club, Membership
from .forms import SignUpForm, ProfileForm, ClubForm, MembershipForm, MemberFormSet, FormSetHelper
from .tables import ClubTable, UserTable
from .filters import UserFilter, UserFilterFormHelper


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
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
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
            # Si le nouveau pseudo n'est pas un de nos alias, on supprime éventuellement un alias similaire pour le remplacer
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
            return reverse_lazy('member:user_detail', args=(self.object.id, ))


class UserDetailView(LoginRequiredMixin, DetailView):
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
            Transaction.objects.all().filter(Q(source=user.note) | Q(destination=user.note))
        context['history_list'] = HistoryTable(history_list)
        club_list = \
            Membership.objects.all().filter(user=user).only("club")
        context['club_list'] = ClubTable(club_list)
        context['title'] = _("Account #%(id)s: %(username)s") % {
            'id': user.pk,
            'username': user.username,
        }
        return context


class UserListView(LoginRequiredMixin, SingleTableView):
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

class AliasView(LoginRequiredMixin,FormMixin,DetailView):
    model = User
    template_name = 'member/profile_alias.html'
    context_object_name = 'user_object'
    form_class = AliasForm

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        note = context['user_object'].note
        context["aliases"] = AliasTable(note.alias_set.all())
        return context

    def get_success_url(self):
        return reverse_lazy('member:user_alias', kwargs={'pk': self.object.id})

    def post(self,request,*args,**kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        alias = form.save(commit=False)
        alias.note = self.object.note
        alias.save()
        return super().form_valid(form)

class DeleteAliasView(LoginRequiredMixin, DeleteView):
    model = Alias

    def delete(self,request,*args,**kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
        except ValidationError as e:
            # TODO: pass message to redirected view.
            messages.error(self.request,str(e))
        else:
            messages.success(self.request,_("Alias successfully deleted"))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        print(self.request)
        return reverse_lazy('member:user_alias',kwargs={'pk':self.object.note.user.pk})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class ProfilePictureUpdateView(LoginRequiredMixin, FormMixin, DetailView):
    model = User
    template_name = 'member/profile_picture_update.html'
    context_object_name = 'user_object'
    form_class = ImageForm
    def get_context_data(self,*args,**kwargs):
        context = super().get_context_data(*args,**kwargs)
        context['form'] = self.form_class(self.request.POST,self.request.FILES)
        return context
        
    def get_success_url(self):
        return reverse_lazy('member:user_detail', kwargs={'pk': self.object.id})

    def post(self,request,*args,**kwargs):
        form  = self.get_form()
        self.object = self.get_object()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print('is_invalid')
            print(form)
            return self.form_invalid(form)

    def form_valid(self,form):
        image_file_field = form.cleaned_data['image']
        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        w = form.cleaned_data['width']
        h = form.cleaned_data['height']
        with Image.open(image_file_field.name) as image:
            image = image.crop((x, y, w+x, h+y))
            image.thumbnail((256, 256), Image.ANTIALIAS)
            image.save(image_file_field.name,format=image.format)
        self.object.note.display_image = image_file_field
        self.object.note.save()
        return super().form_valid(form)

class ManageAuthTokens(LoginRequiredMixin, TemplateView):
    """
    Affiche le jeton d'authentification, et permet de le regénérer
    """
    model = Token
    template_name = "member/manage_auth_tokens.html"

    def get(self, request, *args, **kwargs):
        if 'regenerate' in request.GET and Token.objects.filter(
                user=request.user).exists():
            Token.objects.get(user=self.request.user).delete()
            return redirect(reverse_lazy('member:auth_token') + "?show",
                            permanent=True)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = Token.objects.get_or_create(
            user=self.request.user)[0]
        return context


class UserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Auto complete users by usernames
    """
    def get_queryset(self):
        """
        Quand une personne cherche un utilisateur par pseudo, une requête est envoyée sur l'API dédiée à l'auto-complétion.
        Cette fonction récupère la requête, et renvoie la liste filtrée des utilisateurs par pseudos.
        """
        #  Un utilisateur non connecté n'a accès à aucune information
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.all()

        if self.q:
            qs = qs.filter(username__regex=self.q)

        return qs


# ******************************* #
#              CLUB               #
# ******************************* #


class ClubCreateView(LoginRequiredMixin, CreateView):
    """
    Create Club
    """
    model = Club
    form_class = ClubForm

    def form_valid(self, form):
        return super().form_valid(form)


class ClubListView(LoginRequiredMixin, SingleTableView):
    """
    List existing Clubs
    """
    model = Club
    table_class = ClubTable


class ClubDetailView(LoginRequiredMixin, DetailView):
    model = Club
    context_object_name = "club"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = context["club"]
        club_transactions =  \
            Transaction.objects.all().filter(Q(source=club.note) | Q(destination=club.note))
        context['history_list'] = HistoryTable(club_transactions)
        club_member = \
            Membership.objects.all().filter(club=club)
        # TODO: consider only valid Membership
        context['member_list'] = club_member
        return context


class ClubAddMemberView(LoginRequiredMixin, CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'member/add_members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = MemberFormSet()
        context['helper'] = FormSetHelper()

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
