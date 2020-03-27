# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from activity.models import Activity
from note_kfet.inputs import DateTimePickerInput


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'
        widgets = {
            "date_start": DateTimePickerInput(),
            "date_end": DateTimePickerInput(),
        }
