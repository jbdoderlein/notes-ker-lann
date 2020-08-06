# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
from note.models import NoteSpecial, Alias
from note_kfet.inputs import Autocomplete, AmountInput, DatePickerInput
from permission.models import PermissionMask, Role

from .models import Profile, Club, Membership


class CustomAuthenticationForm(AuthenticationForm):
    permission_mask = forms.ModelChoiceField(
        label="Masque de permissions",
        queryset=PermissionMask.objects.order_by("rank"),
        empty_label=None,
    )


class UserForm(forms.ModelForm):
    def _get_validation_exclusions(self):
        # Django usernames can only contain letters, numbers, @, ., +, - and _.
        # We want to allow users to have uncommon and unpractical usernames:
        # That is their problem, and we have normalized aliases for us.
        return super()._get_validation_exclusions() + ["username"]

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)


class ProfileForm(forms.ModelForm):
    """
    A form for the extras field provided by the :model:`member.Profile` model.
    """
    report_frequency = forms.IntegerField(required=False, initial=0, label=_("Report frequency"))

    last_report = forms.DateField(required=False, disabled=True, label=_("Last report date"))

    def save(self, commit=True):
        if not self.instance.section or (("department" in self.changed_data
                                         or "promotion" in self.changed_data) and "section" not in self.changed_data):
            self.instance.section = self.instance.section_generated
        return super().save(commit)

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ('user', 'email_confirmed', 'registration_valid', )


class ClubForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        if not self.instance.pk:    # Creating a club
            if Alias.objects.filter(normalized_name=Alias.normalize(self.cleaned_data["name"])).exists():
                self.add_error('name', _("An alias with a similar name already exists."))

        return cleaned_data

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
        fields = ('user', 'date_start')
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


class MembershipRolesForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects,
        label=_("User"),
        disabled=True,
        widget=Autocomplete(
            User,
            attrs={
                'api_url': '/api/user/',
                'name_field': 'username',
                'placeholder': 'Nom ...',
            },
        ),
    )

    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.filter(weirole=None).all(),
        label=_("Roles"),
        widget=CheckboxSelectMultiple(),
    )

    class Meta:
        model = Membership
        fields = ('user', 'roles')
