# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from member.models import Club
from note.models import NoteUser, Note
from note_kfet.inputs import DateTimePickerInput, Autocomplete

from .models import Activity, Guest


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        exclude = ('creater', 'valid', 'open', )
        widgets = {
            "organizer": Autocomplete(
                model=Club,
                attrs={"api_url": "/api/members/club/"},
            ),
            "note": Autocomplete(
                model=Note,
                attrs={
                    "api_url": "/api/note/note/",
                    'placeholder': 'Note de l\'événement sur laquelle envoyer les crédits d\'invitation ...'
                },
            ),
            "attendees_club": Autocomplete(
                model=Club,
                attrs={"api_url": "/api/members/club/"},
            ),
            "date_start": DateTimePickerInput(),
            "date_end": DateTimePickerInput(),
        }


class GuestForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        if self.activity.date_start > timezone.now():
            self.add_error("inviter", _("You can't invite someone once the activity is started."))

        if not self.activity.valid:
            self.add_error("inviter", _("This activity is not validated yet."))

        one_year = timedelta(days=365)

        qs = Guest.objects.filter(
            first_name=cleaned_data["first_name"],
            last_name=cleaned_data["last_name"],
            activity__date_start__gte=self.activity.date_start - one_year,
        )
        if len(qs) >= 5:
            self.add_error("last_name", _("This person has been already invited 5 times this year."))

        qs = qs.filter(activity=self.activity)
        if qs.exists():
            self.add_error("last_name", _("This person is already invited."))

        qs = Guest.objects.filter(inviter=cleaned_data["inviter"], activity=self.activity)
        if len(qs) >= 3:
            self.add_error("inviter", _("You can't invite more than 3 people to this activity."))

        return cleaned_data

    class Meta:
        model = Guest
        fields = ('last_name', 'first_name', 'inviter', )
        widgets = {
            "inviter": Autocomplete(
                NoteUser,
                attrs={
                    'api_url': '/api/note/note/',
                    # We don't evaluate the content type at launch because the DB might be not initialized
                    'api_url_suffix':
                        lambda: '&polymorphic_ctype=' + str(ContentType.objects.get_for_model(NoteUser).pk),
                    'placeholder': 'Note ...',
                },
            ),
        }
