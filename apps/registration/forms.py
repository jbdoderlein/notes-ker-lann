# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from note.models import NoteSpecial, Alias
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

        # Give some example
        self.fields['first_name'].widget.attrs.update({"placeholder": "Sacha"})
        self.fields['last_name'].widget.attrs.update({"placeholder": "Ketchum"})
        self.fields['email'].widget.attrs.update({"placeholder": "mail@example.com"})

    def clean_username(self):
        value = self.cleaned_data["username"]
        if Alias.objects.filter(normalized_name=Alias.normalize(value)).exists():
            self.add_error("username", _("An alias with a similar name already exists."))
        return value

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            self.add_error("email", _("This email address is already used."))
        return email

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', )


class DeclareSogeAccountOpenedForm(forms.Form):
    soge_account = forms.BooleanField(
        label=_("I declare that I opened a bank account in the Société générale with the BDE partnership."),
        help_text=_("Warning: this engages you to open your bank account. If you finally decides to don't open your "
                    "account, you will have to pay the BDE membership."),
        required=False,
    )


class WEISignupForm(forms.Form):
    wei_registration = forms.BooleanField(
        label=_("Register to the WEI"),
        required=False,
        help_text=_("Check this case if you want to register to the WEI. If you hesitate, you will be able to register"
                    " later, after validating your account in the Kfet."),
    )


class ValidationForm(forms.Form):
    """
    Validate the inscription of the new users and pay memberships.
    """
    soge = forms.BooleanField(
        label=_("Inscription paid by Société Générale"),
        required=False,
        help_text=_("Check this case if the Société Générale paid the inscription."),
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

    join_bde = forms.BooleanField(
        label=_("Join BDE Club"),
        required=False,
        initial=True,
    )

    # The user can join the Kfet club at the inscription
    join_kfet = forms.BooleanField(
        label=_("Join Kfet Club"),
        required=False,
        initial=True,
    )
