# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from dal import autocomplete
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Alias
from .models import Transaction, TransactionTemplate


class AliasForm(forms.ModelForm):
    class Meta:
        model = Alias
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = False
        self.fields["name"].widget.attrs = {"placeholder": _('New Alias')}


class ImageForm(forms.Form):
    image = forms.ImageField(required=False,
                             label=_('select an image'),
                             help_text=_('Maximal size: 2MB'))
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())


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
