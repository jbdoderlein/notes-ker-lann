# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
import time
from random import Random

from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .base import WEISurvey, WEISurveyInformation, WEISurveyAlgorithm, WEIBusInformation

WORDS = [
    '13 organisé', '3ième mi temps', 'Années 2000', 'Apéro', 'BBQ', 'BP', 'Beauf', 'Binge drinking', 'Bon enfant',
    'Cartouche', 'Catacombes', 'Chansons paillardes', 'Chansons populaires', 'Chanteur', 'Chartreuse', 'Chill',
    'Core', 'DJ', 'Dancefloor', 'Danse', 'David Guetta', 'Disco', 'Eau de vie', 'Électro', 'Escalade', 'Familial',
    'Fanfare', 'Fracassage', 'Féria', 'Hard rock', 'Hoeggarden', 'House', 'Huit-six', 'IPA', 'Inclusif', 'Inferno',
    'Introverti', 'Jager bomb', 'Jazz', 'Jeux d\'alcool', 'Jeux de rôles', 'Jeux vidéo', 'Jul', 'Jus de fruit',
    'Karaoké', 'LGBTQI+', 'Lady Gaga', 'Loup garou', 'Morning beer', 'Métal', 'Nuit blanche', 'Ovalie', 'Psychedelic',
    'Pétanque', 'Rave', 'Reggae', 'Rhum', 'Ricard', 'Rock', 'Rosé', 'Rétro', 'Séducteur', 'Techno', 'Thérapie taxi',
    'Théâtre', 'Trap', 'Turn up', 'Underground', 'Volley', 'Wati B', 'Zinédine Zidane',
]


class WEISurveyForm2021(forms.Form):
    """
    Survey form for the year 2021.
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
        information = WEISurveyInformation2021(registration)
        if not information.seed:
            information.seed = int(1000 * time.time())
            information.save(registration)
            registration._force_save = True
            registration.save()

        rng = Random(information.seed)

        words = None
        # Update seed
        rng.randint(0, information.step)

        preferred_words = {bus: [word for word in WORDS if bus.size > 0
                                 and WEIBusInformation2021(bus).scores[word] >= 50]
                           for bus in WEISurveyAlgorithm2021.get_buses()}
        while words is None or len(set(words)) != len(words):
            # Ensure that there is no the same word 2 times
            words = [rng.choice(words) for _ignored2, words in preferred_words.items()]
        rng.shuffle(words)
        words = [(w, w) for w in words]
        if self.data:
            self.fields["word"].choices = [(w, w) for w in WORDS]
            if self.is_valid():
                return
        self.fields["word"].choices = words


class WEIBusInformation2021(WEIBusInformation):
    """
    For each word, the bus has a score
    """
    scores: dict

    def __init__(self, bus):
        self.scores = {}
        for word in WORDS:
            self.scores[word] = 0.0
        super().__init__(bus)


class WEISurveyInformation2021(WEISurveyInformation):
    """
    We store the id of the selected bus. We store only the name, but is not used in the selection:
    that's only for humans that try to read data.
    """
    # Random seed that is stored at the first time to ensure that words are generated only once
    seed = 0
    step = 0

    def __init__(self, registration):
        for i in range(1, 21):
            setattr(self, "word" + str(i), None)
        super().__init__(registration)


class WEISurvey2021(WEISurvey):
    """
    Survey for the year 2021.
    """

    @classmethod
    def get_year(cls):
        return 2021

    @classmethod
    def get_survey_information_class(cls):
        return WEISurveyInformation2021

    def get_form_class(self):
        return WEISurveyForm2021

    def update_form(self, form):
        """
        Filter the bus selector with the buses of the WEI.
        """
        form.set_registration(self.registration)

    @transaction.atomic
    def form_valid(self, form):
        word = form.cleaned_data["word"]
        self.information.step += 1
        setattr(self.information, "word" + str(self.information.step), word)
        self.save()

    @classmethod
    def get_algorithm_class(cls):
        return WEISurveyAlgorithm2021

    def is_complete(self) -> bool:
        """
        The survey is complete once the bus is chosen.
        """
        return self.information.step == 20

    def score(self, bus):
        if not self.is_complete():
            raise ValueError("Survey is not ended, can't calculate score")
        bus_info = self.get_algorithm_class().get_bus_information(bus)
        return sum(bus_info.scores[getattr(self.information, 'word' + str(i))] for i in range(1, 21)) / 20

    def scores_per_bus(self):
        return {bus: self.score(bus) for bus in self.get_algorithm_class().get_buses()}

    def ordered_buses(self):
        values = list(self.scores_per_bus().items())
        values.sort(key=lambda item: -item[1])
        return values


class WEISurveyAlgorithm2021(WEISurveyAlgorithm):
    """
    The algorithm class for the year 2021.
    We use Gale-Shapley algorithm to attribute 1y students into buses.
    """

    @classmethod
    def get_survey_class(cls):
        return WEISurvey2021

    @classmethod
    def get_bus_information_class(cls):
        return WEIBusInformation2021

    def run_algorithm(self):
        """
        Gale-Shapley algorithm implementation.
        We modify it to allow buses to have multiple "weddings".
        """
        surveys = list(self.get_survey_class()(r) for r in self.get_registrations())  # All surveys
        free_surveys = [s for s in surveys if not s.information.valid]  # Remaining surveys
        while free_surveys:  # Some students are not affected
            survey = free_surveys[0]
            buses = survey.ordered_buses()  # Preferences of the student
            for bus, _ignored in buses:
                if self.get_bus_information(bus).has_free_seats(surveys):
                    # Selected bus has free places. Put student in the bus
                    survey.select_bus(bus)
                    survey.save()
                    free_surveys.remove(survey)
                    break
                else:
                    # Current bus has not enough places. Remove the least preferred student from the bus if existing
                    current_score = survey.score(bus)
                    least_preferred_survey = None
                    least_score = -1
                    # Find the least student in the bus that has a lower score than the current student
                    for survey2 in surveys:
                        if not survey2.information.valid or survey2.information.get_selected_bus() != bus:
                            continue
                        score2 = survey2.score(bus)
                        if current_score <= score2:  # Ignore better students
                            continue
                        if least_preferred_survey is None or score2 < least_score:
                            least_preferred_survey = survey2
                            least_score = score2

                    if least_preferred_survey is not None:
                        # Remove the least student from the bus and put the current student in.
                        # If it does not exist, choose the next bus.
                        least_preferred_survey.free()
                        least_preferred_survey.save()
                        free_surveys.append(least_preferred_survey)
                        survey.select_bus(bus)
                        survey.save()
                        break
            else:
                raise ValueError(f"User {survey.registration.user} has no free seat")
