# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from member.models import Club
from note.models import NoteUser
from note_kfet.inputs import DateTimePickerInput, AutocompleteModelSelect

from .models import Activity, Guest


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'
        widgets = {
            "organizer": AutocompleteModelSelect(
                model=Club,
                attrs={"api_url": "/api/members/club/"},
            ),
            "attendees_club": AutocompleteModelSelect(
                model=Club,
                attrs={"api_url": "/api/members/club/"},
            ),
            "date_start": DateTimePickerInput(),
            "date_end": DateTimePickerInput(),
        }


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ('last_name', 'first_name', 'inviter', )
        widgets = {
            "inviter": AutocompleteModelSelect(
                NoteUser,
                attrs={
                    'api_url': '/api/note/note/',
                    # We don't evaluate the content type at launch because the DB might be not initialized
                    'api_url_suffix':
                        lambda value: '&polymorphic_ctype=' + str(ContentType.objects.get_for_model(NoteUser).pk),
                    'placeholder': 'Note ...',
                },
            ),
        }
