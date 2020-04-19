# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from django.db.models import QuerySet
from django.forms import Form

from ...models import WEIClub, WEIRegistration, Bus


class WEISurveyInformation:
    """
    Abstract data of the survey.
    """
    valid = False
    selected_bus_pk = None
    selected_bus_name = None

    def __init__(self, registration):
        self.__dict__.update(registration.information)

    def get_selected_bus(self) -> Optional[Bus]:
        """
        If the algorithm ran, return the prefered bus according to the survey.
        In the other case, return None.
        """
        if not self.valid:
            return None
        return Bus.objects.get(pk=self.selected_bus_pk)

    def save(self, registration) -> None:
        """
        Store the data of the survey into the database, with the information of the registration.
        """
        registration.information = self.__dict__
        registration.save()


class WEISurveyAlgorithm:
    """
    Abstract algorithm that attributes a bus to each new member.
    """

    @classmethod
    def get_survey_class(cls):
        """
        The class of the survey associated with this algorithm.
        """
        raise NotImplementedError

    @classmethod
    def get_registrations(cls) -> QuerySet:
        """
        Queryset of all first year registrations
        """
        return WEIRegistration.objects.filter(wei__year=cls.get_survey_class().get_year(), first_year=True)

    @classmethod
    def get_buses(cls) -> QuerySet:
        """
        Queryset of all buses of the associated wei.
        """
        return Bus.objects.filter(wei__year=cls.get_survey_class().get_year())

    def run_algorithm(self) -> None:
        """
        Once this method implemented, run the algorithm that attributes a bus to each first year member.
        This method can be run in command line through ``python manage.py wei_algorithm``
        See ``wei.management.commmands.wei_algorithm``
        This method must call Survey.select_bus for each survey.
        """
        raise NotImplementedError


class WEISurvey:
    """
    Survey associated to a first year WEI registration.
    The data is stored into WEISurveyInformation, this class acts as a manager.
    This is an abstract class: this has to be extended each year to implement custom methods.
    """

    def __init__(self, registration: WEIRegistration):
        self.registration = registration
        self.information = self.get_survey_information_class()(registration)

    @classmethod
    def get_year(cls) -> int:
        """
        Get year of the wei concerned by the type of the survey.
        """
        raise NotImplementedError

    @classmethod
    def get_wei(cls) -> WEIClub:
        """
        The WEI associated to this kind of survey.
        """
        return WEIClub.objects.get(year=cls.get_year())

    @classmethod
    def get_survey_information_class(cls):
        """
        The class of the data (extending WEISurveyInformation).
        """
        raise NotImplementedError

    def get_form_class(self) -> Form:
        """
        The form class of the survey.
        This is proper to the status of the survey: the form class can evolve according to the progress of the survey.
        """
        raise NotImplementedError

    def update_form(self, form) -> None:
        """
        Once the form is instanciated, the information can be updated with the information of the registration
        and the information of the survey.
        This method is called once the form is created.
        """
        pass

    def form_valid(self, form) -> None:
        """
        Called when the information of the form are validated.
        This method should update the information of the survey.
        """
        raise NotImplementedError

    def is_complete(self) -> bool:
        """
        Return True if the survey is complete.
        If the survey is complete, then the button "Next" will display some text for the end of the survey.
        If not, the survey is reloaded and continues.
        """
        raise NotImplementedError

    def save(self) -> None:
        """
        Store the information of the survey into the database.
        """
        self.information.save(self.registration)
        self.registration.save()

    @classmethod
    def get_algorithm_class(cls):
        """
        Algorithm class associated to the survey.
        The algorithm, extending WEISurveyAlgorithm, should associate a bus to each first year member.
        The association is not permanent: that's only a suggestion.
        """
        raise NotImplementedError

    def select_bus(self, bus) -> None:
        """
        Set the suggestion into the data of the membership.
        :param bus: The bus suggested.
        """
        self.information.selected_bus_pk = bus.pk
        self.information.selected_bus_name = bus.name
        self.information.valid = True
