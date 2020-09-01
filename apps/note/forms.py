# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from datetime import datetime

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import CheckboxSelectMultiple
from django.utils.timezone import  make_aware
from django.utils.translation import gettext_lazy as _
from note_kfet.inputs import Autocomplete, AmountInput, DateTimePickerInput

from .models import TransactionTemplate, NoteClub, Alias


class TransactionTemplateForm(forms.ModelForm):
    class Meta:
        model = TransactionTemplate
        fields = '__all__'

        widgets = {
            'destination':
                Autocomplete(
                    NoteClub,
                    attrs={
                        'api_url': '/api/note/note/',
                        # We don't evaluate the content type at launch because the DB might be not initialized
                        'api_url_suffix':
                            lambda: '&polymorphic_ctype=' + str(ContentType.objects.get_for_model(NoteClub).pk),
                        'placeholder': 'Note ...',
                    },
                ),
            'amount': AmountInput(),
        }


class SearchTransactionForm(forms.Form):
    source = forms.ModelChoiceField(
        queryset=Alias.objects.all(),
        label=_("Source"),
        required=False,
        widget=Autocomplete(
            Alias,
            resetable=True,
            attrs={
                'api_url': '/api/note/alias/',
                'placeholder': 'Note ...',
            },
        ),
    )

    destination = forms.ModelChoiceField(
        queryset=Alias.objects.all(),
        label=_("Destination"),
        required=False,
        widget=Autocomplete(
            Alias,
            resetable=True,
            attrs={
                'api_url': '/api/note/alias/',
                'placeholder': 'Note ...',
            },
        ),
    )

    type = forms.ModelMultipleChoiceField(
        queryset=ContentType.objects.filter(app_label="note", model__endswith="transaction"),
        initial=ContentType.objects.filter(app_label="note", model__endswith="transaction"),
        label=_("Type"),
        required=False,
        widget=CheckboxSelectMultiple(),
    )

    reason = forms.CharField(
        label=_("Reason"),
        required=False,
    )

    valid = forms.BooleanField(
        label=_("Valid"),
        initial=False,
        required=False,
    )

    amount_gte = forms.Field(
        label=_("Total amount greater than"),
        initial=0,
        required=False,
        widget=AmountInput(),
    )

    amount_lte = forms.Field(
        initial=2 ** 31 - 1,
        label=_("Total amount less than"),
        required=False,
        widget=AmountInput(),
    )

    created_after = forms.DateTimeField(
        label=_("Created after"),
        initial=make_aware(datetime(year=2000, month=1, day=1, hour=0, minute=0)),
        required=False,
        widget=DateTimePickerInput(),
    )

    created_before = forms.DateTimeField(
        label=_("Created before"),
        initial=make_aware(datetime(year=2042, month=12, day=31, hour=21, minute=42)),
        required=False,
        widget=DateTimePickerInput(),
    )
