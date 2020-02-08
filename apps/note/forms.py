#!/usr/bin/env python

from dal import autocomplete
from django import forms
from .models import Transaction, TransactionTemplate

class TransactionTemplateForm(forms.ModelForm):
    class Meta:
        model = TransactionTemplate
        fields ='__all__'

        widgets = {
            'destination': autocomplete.ModelSelect2(url='note:note_autocomplete',
                                                     attrs={
                                                         'data-placeholder': 'Note ...',
                                                         'data-minimum-input-length': 1,
                                                     }),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('destination', 'reason', 'amount',)

        widgets = {
            'destination': autocomplete.ModelSelect2(url='note:note_autocomplete',
                                                     attrs={
                                                         'data-placeholder': 'Note ...',
                                                         'data-minimum-input-length': 1,
                                                     }),
        }

