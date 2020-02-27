# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from dal import autocomplete
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Transaction, TransactionTemplate, TemplateTransaction


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
        super().save(commit)


    def clean(self):
        """
        If the user has no right to transfer funds, then it will be the source of the transfer by default.
        Transactions between a note and the same note are not authorized.
        """

        cleaned_data = super().clean()
        if not "source" in cleaned_data: # TODO Replace it with "if %user has no right to transfer funds"
            cleaned_data["source"] = self.user.note

        if cleaned_data["source"].pk == cleaned_data["destination"].pk:
            self.add_error("destination", _("Source and destination must be different."))

        return cleaned_data


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
        self.instance.reason = '{} ({})'.format(button.name, button.category)
        self.instance.name = button.name
        self.instance.category = button.category
        super().save(commit)

    class Meta:
        model = TemplateTransaction
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
