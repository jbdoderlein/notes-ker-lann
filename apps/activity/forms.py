# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from activity.models import Activity
from member.models import Club
from note_kfet.inputs import DateTimePickerInput, AutocompleteModelSelect


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
