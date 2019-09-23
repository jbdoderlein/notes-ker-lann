#!/usr/bin/env python

# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, DetailView
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.db.models import Q

from django_tables2.views import SingleTableView


from .models import Profile, Club, Membership
from .forms import ProfileForm, ClubForm,MembershipForm, MemberFormSet,FormSetHelper
from .tables import ClubTable,UserTable
from .filters import UserFilter, UserFilterFormHelper


from note.models.transactions import Transaction
from note.tables import HistoryTable

class UserCreateView(CreateView):
    """
    Une vue pour inscrire un utilisateur et lui créer un profile
    """

    form_class = ProfileForm
    success_url = reverse_lazy('login')
    template_name ='member/signup.html'
    second_form = UserCreationForm

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["user_form"] = self.second_form

        return context

    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user_profile = form.save(commit=False) # do not save to db
            user_profile.user = user
            user_profile.save()
        return super().form_valid(form)

class UserDetailView(LoginRequiredMixin,DetailView):
    """
    Affiche les informations sur un utilisateur, sa note, ses clubs ...
    """
    model = Profile
    context_object_name = "profile"
    def get_context_data(slef,**kwargs):
        context = super().get_context_data(**kwargs)
        user = context['profile'].user
        history_list = \
            Transaction.objects.all().filter(Q(source=user.note) | Q(destination=user.note))
        context['history_list'] = HistoryTable(history_list)
        club_list = \
            Membership.objects.all().filter(user=user).only("club")
        context['club_list'] = ClubTable(club_list)
        return context

class UserListView(LoginRequiredMixin,SingleTableView):
    """
    Affiche la liste des utilisateurs, avec une fonction de recherche statique
    """
    model = User
    table_class = UserTable
    template_name = 'member/user_list.html'
    filter_class = UserFilter
    formhelper_class = UserFilterFormHelper

    def get_queryset(self,**kwargs):
        qs = super().get_queryset()
        self.filter = self.filter_class(self.request.GET,queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        return context


###################################
############## CLUB ###############
###################################

class ClubCreateView(LoginRequiredMixin,CreateView):
    """
    Create Club
    """
    model = Club
    form_class = ClubForm

    def form_valid(self,form):
        return super().form_valid(form)

class ClubListView(LoginRequiredMixin,SingleTableView):
    """
    List existing Clubs
    """
    model = Club
    table_class = ClubTable

class ClubDetailView(LoginRequiredMixin,DetailView):
    model = Club
    context_object_name="club"

    def get_context_data(self,**kwargs):
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

class ClubAddMemberView(LoginRequiredMixin,CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'member/add_members.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = MemberFormSet()
        context['helper'] = FormSetHelper()
        return context

    def post(self,request,*args,**kwargs):
        formset = MembershipFormset(request.POST)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self,formset):
        formset.save()
        return super().form_valid(formset)
