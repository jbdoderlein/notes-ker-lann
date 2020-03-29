# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from note_kfet.inputs import Autocomplete

from .models import TransactionTemplate, NoteClub


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
        }
