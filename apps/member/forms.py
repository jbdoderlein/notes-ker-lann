# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile, Club

class ProfileForm(forms.ModelForm):
    """
    Forms pour la création d'un profile utilisateur.
    """
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields ='__all__'
