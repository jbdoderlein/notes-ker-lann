# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from note.models import NoteSpecial
from note_kfet.inputs import Autocomplete, AmountInput, DatePickerInput
from permission.models import PermissionMask

from .models import Profile, Club, Membership, Role


class CustomAuthenticationForm(AuthenticationForm):
    permission_mask = forms.ModelChoiceField(
        label="Masque de permissions",
        queryset=PermissionMask.objects.order_by("rank"),
        empty_label=None,
    )


class ProfileForm(forms.ModelForm):
    """
    A form for the extras field provided by the :model:`member.Profile` model.
    """

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ('user', 'email_confirmed', 'registration_valid', 'soge', )


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = '__all__'
        widgets = {
            "membership_fee_paid": AmountInput(),
            "membership_fee_unpaid": AmountInput(),
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
    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.filter(weirole=None).all())

    soge = forms.BooleanField(
        label=_("Inscription paid by Société Générale"),
        required=False,
        help_text=_("Check this case is the Société Générale paid the inscription."),
    )

    credit_type = forms.ModelChoiceField(
        queryset=NoteSpecial.objects,
        label=_("Credit type"),
        empty_label=_("No credit"),
        required=False,
        help_text=_("You can credit the note of the user."),
    )

    credit_amount = forms.IntegerField(
        label=_("Credit amount"),
        required=False,
        initial=0,
        widget=AmountInput(),
    )

    last_name = forms.CharField(
        label=_("Last name"),
        required=False,
    )

    first_name = forms.CharField(
        label=_("First name"),
        required=False,
    )

    bank = forms.CharField(
        label=_("Bank"),
        required=False,
    )

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
