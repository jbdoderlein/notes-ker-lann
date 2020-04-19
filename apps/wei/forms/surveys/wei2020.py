# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms

from .base import WEISurvey, WEISurveyInformation, WEISurveyAlgorithm
from ...models import Bus


class WEISurveyForm2020(forms.Form):
    """
    Survey form for the year 2020.
    For now, that's only a Bus selector.
    TODO: Do a better survey (later)
    """
    bus = forms.ModelChoiceField(
        Bus.objects,
    )

    def set_registration(self, registration):
        """
        Filter the bus selector with the buses of the current WEI.
        """
        self.fields["bus"].queryset = Bus.objects.filter(wei=registration.wei)


class WEISurveyInformation2020(WEISurveyInformation):
    """
    We store the id of the selected bus. We store only the name, but is not used in the selection:
    that's only for humans that try to read data.
    """
    chosen_bus_pk = None
    chosen_bus_name = None


class WEISurvey2020(WEISurvey):
    """
    Survey for the year 2020.
    """
    @classmethod
    def get_year(cls):
        return 2020

    @classmethod
    def get_survey_information_class(cls):
        return WEISurveyInformation2020

    def get_form_class(self):
        return WEISurveyForm2020

    def update_form(self, form):
        """
        Filter the bus selector with the buses of the WEI.
        """
        form.set_registration(self.registration)

    def form_valid(self, form):
        bus = form.cleaned_data["bus"]
        self.information.chosen_bus_pk = bus.pk
        self.information.chosen_bus_name = bus.name
        self.save()

    @classmethod
    def get_algorithm_class(cls):
        return WEISurveyAlgorithm2020

    def is_complete(self) -> bool:
        """
        The survey is complete once the bus is chosen.
        """
        return self.information.chosen_bus_pk is not None


class WEISurveyAlgorithm2020(WEISurveyAlgorithm):
    """
    The algorithm class for the year 2020.
    For now, the algorithm is quite simple: the selected bus is the chosen bus.
    TODO: Improve this algorithm.
    """

    @classmethod
    def get_survey_class(cls):
        return WEISurvey2020

    def run_algorithm(self):
        for registration in self.get_registrations():
            survey = self.get_survey_class()(registration)
            survey.select_bus(Bus.objects.get(pk=survey.information.chosen_bus_pk))
            survey.save()
