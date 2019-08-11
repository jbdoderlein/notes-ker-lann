#!/usr/bin/env python

# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Profile
from .forms import ProfileForm

class SignUp(CreateView):
    """
    Une vue pour inscrire un utilisateur et lui créer un profile

    """
    form_class = ProfileForm
    success_url = reverse_lazy('login')
    template_name ='member/signup.html'
    second_form = UserCreationForm

    def get_context_data(self,**kwargs):
        context = super(SignUp,self).get_context_data(**kwargs)
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
