#!/usr/bin/env python

from dal import autocomplete, forward
from django import forms
from .models import Transaction, TransactionTemplate


class TransactionTemplateForm(forms.ModelForm):
    class Meta:
        model = TransactionTemplate
        fields = '__all__'

        # Le champ de destination est remplacé par un champ d'auto-complétion.
        # Quand des lettres sont tapées, une requête est envoyée sur l'API d'auto-complétion
        # et récupère les aliases valides
        # Pour force le type d'une note, il faut rajouter le paramètre :
        # forward=(forward.Const('TYPE', 'note_type') où TYPE est dans {user, club, special}
        widgets = {
            'destination':
            autocomplete.ModelSelect2(
                url='note:note_autocomplete',
                attrs={
                    'data-placeholder': 'Note ...',
                    'data-minimum-input-length': 1,
                },
            ),
        }


class TransactionForm(forms.ModelForm):
    def save(self, commit=True):
        self.instance.transaction_type = 'transfert'

        super().save(commit)

    class Meta:
        model = Transaction
        fields = (
            'source',
            'destination',
            'reason',
            'amount',
        )

        # Voir ci-dessus
        widgets = {
            'source':
            autocomplete.ModelSelect2(
                url='note:note_autocomplete',
                attrs={
                    'data-placeholder': 'Note ...',
                    'data-minimum-input-length': 1,
                },
            ),
            'destination':
            autocomplete.ModelSelect2(
                url='note:note_autocomplete',
                attrs={
                    'data-placeholder': 'Note ...',
                    'data-minimum-input-length': 1,
                },
            ),
        }


class ConsoForm(forms.ModelForm):
    def save(self, commit=True):
        button: TransactionTemplate = TransactionTemplate.objects.filter(
            name=self.data['button']).get()
        self.instance.destination = button.destination
        self.instance.amount = button.amount
        self.instance.transaction_type = 'bouton'
        self.instance.reason = button.name
        super().save(commit)

    class Meta:
        model = Transaction
        fields = ('source', )

        # Le champ d'utilisateur est remplacé par un champ d'auto-complétion.
        # Quand des lettres sont tapées, une requête est envoyée sur l'API d'auto-complétion
        # et récupère les aliases de note valides
        widgets = {
            'source':
            autocomplete.ModelSelect2(
                url='note:note_autocomplete',
                attrs={
                    'data-placeholder': 'Note ...',
                    'data-minimum-input-length': 1,
                },
            ),
        }
