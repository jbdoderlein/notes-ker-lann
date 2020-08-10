# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from random import choice

from django import forms
from django.utils.translation import gettext_lazy as _

from .base import WEISurvey, WEISurveyInformation, WEISurveyAlgorithm, WEIBusInformation
from ...models import Bus


# TODO: Use new words
WORDS = ['Rap', 'Retro', 'DJ', 'Rock', 'Jazz', 'Chansons Populaires', 'Chansons Paillardes', 'Pop', 'Fanfare',
         'Biere', 'Pastis', 'Vodka', 'Cocktails', 'Eau', 'Sirop', 'Jus de fruit', 'Binge Drinking', 'Rhum',
         'Eau de vie', 'Apéro', 'Morning beer', 'Huit-six', 'Jeux de societé', 'Jeux de cartes', 'Danse', 'Karaoké',
         'Bière Pong', 'Poker', 'Loup Garou', 'Films', "Jeux d'alcool", 'Sport', 'Rangées de cul', 'Chips', 'BBQ',
         'Kebab', 'Saucisse', 'Vegan', 'Vege', 'LGBTIQ+', 'Dab', 'Solitaire', 'Séducteur', 'Sociale', 'Chanteur',
         'Se lacher', 'Chill', 'Débile', 'Beauf', 'Bon enfant']


class WEISurveyForm2020(forms.Form):
    """
    Survey form for the year 2020.
    Members choose 20 words, from which we calculate the best associated bus.
    """

    word = forms.ChoiceField(
        label=_("Choose a word:"),
        widget=forms.RadioSelect(),
    )

    def set_registration(self, registration):
        """
        Filter the bus selector with the buses of the current WEI.
        """
        words = [choice(WORDS) for _ in range(10)]
        words = [(w, w) for w in words]
        if self.data:
            self.fields["word"].choices = [(w, w) for w in WORDS]
            if self.is_valid():
                return
        self.fields["word"].choices = words


class WEIBusInformation2020(WEIBusInformation):
    """
    For each word, the bus has a score
    """
    def __init__(self, bus):
        for word in WORDS:
            setattr(self, word, 0.0)
        super().__init__(bus)


class WEISurveyInformation2020(WEISurveyInformation):
    """
    We store the id of the selected bus. We store only the name, but is not used in the selection:
    that's only for humans that try to read data.
    """
    step = 0

    def __init__(self, registration):
        for i in range(1, 21):
            setattr(self, "word" + str(i), None)
        super().__init__(registration)


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
        word = form.cleaned_data["word"]
        self.information.step += 1
        setattr(self.information, "word" + str(self.information.step), word)
        self.save()

    @classmethod
    def get_algorithm_class(cls):
        return WEISurveyAlgorithm2020

    def is_complete(self) -> bool:
        """
        The survey is complete once the bus is chosen.
        """
        return self.information.step == 20


class WEISurveyAlgorithm2020(WEISurveyAlgorithm):
    """
    The algorithm class for the year 2020.
    For now, the algorithm is quite simple: the selected bus is the chosen bus.
    TODO: Improve this algorithm.
    """

    @classmethod
    def get_survey_class(cls):
        return WEISurvey2020

    @classmethod
    def get_bus_information_class(cls):
        return WEIBusInformation2020

    def run_algorithm(self):
        for registration in self.get_registrations():
            survey = self.get_survey_class()(registration)
            survey.select_bus(choice(Bus.objects.all()))
            survey.save()
