# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from wei.models import WEIClub, WEIRegistration


class WEISurvey:
    year = None
    step = 0

    def __init__(self, registration):
        self.registration = registration
        self.information = self.get_survey_information_class()(registration)

    def get_wei(self):
        return WEIClub.objects.get(year=self.year)

    def get_survey_information_class(self):
        raise NotImplementedError

    def get_form_class(self):
        raise NotImplementedError

    def update_form(self, form):
        pass

    @staticmethod
    def get_algorithm_class():
        raise NotImplementedError

    def form_valid(self, form):
        raise NotImplementedError

    def save(self):
        self.information.save(self.registration)

    def select_bus(self, bus_pk):
        self.information.selected_bus_pk = bus_pk


class WEISurveyInformation:
    valid = False
    selected_bus_pk = None

    def __init__(self, registration):
        self.__dict__.update(registration.information)

    def save(self, registration):
        registration.information = self.__dict__
        registration.save()


class WEISurveyAlgorithm:
    def get_survey_class(self):
        raise NotImplementedError

    def get_registrations(self):
        return WEIRegistration.objects.filter(wei__year=self.get_survey_class().year, first_year=True).all()

    def run_algorithm(self):
        raise NotImplementedError
