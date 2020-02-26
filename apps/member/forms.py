# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from dal import autocomplete
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile, Club, Membership

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import Div
from crispy_forms.layout import Layout


class SignUpForm(UserCreationForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].widget.attrs.pop("autofocus", None)
        self.fields['first_name'].widget.attrs.update({"autofocus":"autofocus"})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class ProfileForm(forms.ModelForm):
    """
    A form for the extras field provided by the :model:`member.Profile` model.
    """
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = '__all__'


class AddMembersForm(forms.Form):
    class Meta:
        fields = ('', )


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ('user', 'roles', 'date_start')
        # Le champ d'utilisateur est remplacé par un champ d'auto-complétion.
        # Quand des lettres sont tapées, une requête est envoyée sur l'API d'auto-complétion
        # et récupère les noms d'utilisateur valides
        widgets = {
            'user':
            autocomplete.ModelSelect2(
                url='member:user_autocomplete',
                attrs={
                    'data-placeholder': 'Nom ...',
                    'data-minimum-input-length': 1,
                },
            ),
        }


MemberFormSet = forms.modelformset_factory(
    Membership,
    form=MembershipForm,
    extra=2,
    can_delete=True,
)


class FormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.form_method = 'POST'
        self.form_class = 'form-inline'
        # self.template = 'bootstrap/table_inline_formset.html'
        self.layout = Layout(
            Div(
                Div('user', css_class='col-sm-2'),
                Div('roles', css_class='col-sm-2'),
                Div('date_start', css_class='col-sm-2'),
                css_class="row formset-row",
            ))
