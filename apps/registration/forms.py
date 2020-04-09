# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from note.models import NoteSpecial
from note_kfet.inputs import AmountInput


class SignUpForm(UserCreationForm):
    """
    Pre-register users with all information
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop("autofocus", None)
        self.fields['first_name'].widget.attrs.update({"autofocus": "autofocus"})
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['email'].help_text = _("This address must be valid.")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', )


class ValidationForm(forms.Form):
    """
    Validate the inscription of the new users and pay memberships.
    """
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

    join_BDE = forms.BooleanField(
        label=_("Join BDE Club"),
        required=False,
        initial=True,
    )

    # The user can join the Kfet club at the inscription
    join_Kfet = forms.BooleanField(
        label=_("Join Kfet Club"),
        required=False,
        initial=True,
    )