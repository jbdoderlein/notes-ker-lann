# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from note_kfet.inputs import AmountInput, DatePickerInput

from .models import WEIClub


class WEIForm(forms.ModelForm):
    class Meta:
        model = WEIClub
        exclude = ('parent_club', 'require_memberships', 'membership_duration', )
        widgets = {
            "membership_fee_paid": AmountInput(),
            "membership_fee_unpaid": AmountInput(),
            "membership_start": DatePickerInput(),
            "membership_end": DatePickerInput(),
            "date_start": DatePickerInput(),
            "date_end": DatePickerInput(),
        }
