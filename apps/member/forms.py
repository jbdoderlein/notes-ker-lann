# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile, Club, Membership

from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms import layout, bootstrap
from crispy_forms.bootstrap import InlineField, FormActions, StrictButton, Div, Field
from crispy_forms.layout import Layout


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

class AddMembersForm(forms.Form):
    class Meta:
        fields = ('',)

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ('user','roles','date_start')

MemberFormSet = forms.modelformset_factory(Membership,
                                           form=MembershipForm,
                                           extra=2,
                                           can_delete=True)

class FormSetHelper(FormHelper):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.form_tag = False
        self.form_method = 'POST'
        self.form_class='form-inline'
        # self.template = 'bootstrap/table_inline_formset.html'
        self.layout = Layout(
            Div(
                Div('user',css_class='col-sm-2'),
                Div('roles',css_class='col-sm-2'),
                Div('date_start',css_class='col-sm-2'),
                css_class="row formset-row",
            )
        )
