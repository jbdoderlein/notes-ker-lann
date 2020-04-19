# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms

from .base import WEISurvey, WEISurveyInformation, WEISurveyAlgorithm
from ...models import Bus


class WEISurveyForm2020(forms.Form):
    bus = forms.ModelChoiceField(
        Bus.objects,
    )

    def set_registration(self, registration):
        self.fields["bus"].queryset = Bus.objects.filter(wei=registration.wei)


class WEISurveyInformation2020(WEISurveyInformation):
    chosen_bus_pk = None
    chosen_bus_name = None


class WEISurvey2020(WEISurvey):
    year = 2020

    def get_survey_information_class(self):
        return WEISurveyInformation2020

    def get_form_class(self):
        return WEISurveyForm2020

    def update_form(self, form):
        form.set_registration(self.registration)

    def form_valid(self, form):
        bus = form.cleaned_data["bus"]
        self.information.chosen_bus_pk = bus.pk
        self.information.chosen_bus_name = bus.name
        self.save()

    @staticmethod
    def get_algorithm_class():
        return WEISurveyAlgorithm2020


class WEISurveyAlgorithm2020(WEISurveyAlgorithm):
    def get_survey_class(self):
        return WEISurvey2020

    def run_algorithm(self):
        for registration in self.get_registrations():
            survey = self.get_survey_class()(registration)
            survey.select_bus(Bus.objects.get(pk=survey.information.chosen_bus_pk))
            survey.save()
