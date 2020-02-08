#!/usr/bin/env python

from dal import autocomplete
from django import forms
from .models import Transaction, TransactionTemplate

class TransactionTemplateForm(forms.ModelForm):
    class Meta:
        model = TransactionTemplate
        fields ='__all__'

        # Le champ de destination est remplacé par un champ d'auto-complétion.
        # Quand des lettres sont tapées, une requête est envoyée sur l'API d'auto-complétion
        # et récupère les aliases valides
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

        # Voir ci-dessus
        widgets = {
            'source': autocomplete.ModelSelect2(url='note:note_autocomplete',
                                                     attrs={
                                                         'data-placeholder': 'Note ...',
                                                         'data-minimum-input-length': 1,
                                                     }),
            'destination': autocomplete.ModelSelect2(url='note:note_autocomplete',
                                                     attrs={
                                                         'data-placeholder': 'Note ...',
                                                         'data-minimum-input-length': 1,
                                                     }),
        }

