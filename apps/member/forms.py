# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from note_kfet.inputs import Autocomplete, AmountInput, DatePickerInput
from permission.models import PermissionMask

from .models import Profile, Club, Membership


class CustomAuthenticationForm(AuthenticationForm):
    permission_mask = forms.ModelChoiceField(
        label="Masque de permissions",
        queryset=PermissionMask.objects.order_by("rank"),
        empty_label=None,
    )


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop("autofocus", None)
        self.fields['first_name'].widget.attrs.update({"autofocus": "autofocus"})

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
        widgets = {
            "membership_fee": AmountInput(),
            "parent_club": Autocomplete(
                Club,
                attrs={
                    'api_url': '/api/members/club/',
                }
            ),
            "membership_start": DatePickerInput(),
            "membership_end": DatePickerInput(),
        }


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ('user', 'roles', 'date_start')
        # Le champ d'utilisateur est remplacé par un champ d'auto-complétion.
        # Quand des lettres sont tapées, une requête est envoyée sur l'API d'auto-complétion
        # et récupère les noms d'utilisateur valides
        widgets = {
            'user':
                Autocomplete(
                    User,
                    attrs={
                        'api_url': '/api/user/',
                        'name_field': 'username',
                        'placeholder': 'Nom ...',
                    },
                ),
            'date_start': DatePickerInput(),
        }
