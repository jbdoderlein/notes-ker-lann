# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta
from random import shuffle

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from member.models import Club
from note.models import Note, NoteUser
from note_kfet.inputs import Autocomplete, DateTimePickerInput
from note_kfet.middlewares import get_current_authenticated_user
from permission.backends import PermissionBackend

from .models import Activity, Guest


class ActivityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # By default, the Kfet club is attended
        self.fields["attendees_club"].initial = Club.objects.get(name="Kfet")
        self.fields["attendees_club"].widget.attrs["placeholder"] = "Kfet"
        clubs = list(Club.objects.filter(PermissionBackend
                                         .filter_queryset(get_current_authenticated_user(), Club, "view")).all())
        shuffle(clubs)
        self.fields["organizer"].widget.attrs["placeholder"] = ", ".join(club.name for club in clubs[:4]) + ", ..."

    def clean_date_end(self):
        date_end = self.cleaned_data["date_end"]
        date_start = self.cleaned_data["date_start"]
        if date_end < date_start:
            self.add_error("date_end", _("The end date must be after the start date."))
        return date_end

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
        """
        Someone can be invited as a Guest to an Activity if:
        - the activity has not already started.
        - the activity is validated.
        - the Guest has not already been invited more than 5 times.
        - the Guest is already invited.
        - the inviter already invited 3 peoples.
        """

        cleaned_data = super().clean()

        if timezone.now() > timezone.localtime(self.activity.date_start):
            self.add_error("inviter", _("You can't invite someone once the activity is started."))

        if not self.activity.valid:
            self.add_error("inviter", _("This activity is not validated yet."))

        one_year = timedelta(days=365)

        qs = Guest.objects.filter(
            first_name__iexact=cleaned_data["first_name"],
            last_name__iexact=cleaned_data["last_name"],
            activity__date_start__gte=self.activity.date_start - one_year,
        )
        if qs.filter(entry__isnull=False).count() >= 5:
            self.add_error("last_name", _("This person has been already invited 5 times this year."))

        qs = qs.filter(activity=self.activity)
        if qs.exists():
            self.add_error("last_name", _("This person is already invited."))

        if "inviter" in cleaned_data:
            if Guest.objects.filter(inviter=cleaned_data["inviter"], activity=self.activity).count() >= 3:
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
