# Copyright (C) 2018-2022 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import random

from django.contrib.auth.models import User
from django.test import TestCase

from ..forms.surveys.wei2022 import WEIBusInformation2022, WEISurvey2022, WORDS, WEISurveyInformation2022
from ..models import Bus, WEIClub, WEIRegistration


class TestWEIAlgorithm(TestCase):
    """
    Run some tests to ensure that the WEI algorithm is working well.
    """
    fixtures = ('initial',)

    def setUp(self):
        """
        Create some test data, with one WEI and 10 buses with random score attributions.
        """
        self.wei = WEIClub.objects.create(
            name="WEI 2022",
            email="wei2022@example.com",
            date_start='2022-09-16',
            date_end='2022-09-18',
            year=2022,
        )

        self.buses = []
        for i in range(10):
            bus = Bus.objects.create(wei=self.wei, name=f"Bus {i}", size=10)
            self.buses.append(bus)
            information = WEIBusInformation2022(bus)
            for word in WORDS:
                information.scores[word] = random.randint(0, 101)
            information.save()
            bus.save()

    def test_survey_algorithm_small(self):
        """
        There are only a few people in each bus, ensure that each person has its best bus
        """
        # Add a few users
        for i in range(10):
            user = User.objects.create(username=f"user{i}")
            registration = WEIRegistration.objects.create(
                user=user,
                wei=self.wei,
                first_year=True,
                birth_date='2000-01-01',
            )
            information = WEISurveyInformation2022(registration)
            for j in range(1, 21):
                setattr(information, f'word{j}', random.choice(WORDS))
            information.step = 20
            information.save(registration)
            registration.save()

        # Run algorithm
        WEISurvey2022.get_algorithm_class()().run_algorithm()

        # Ensure that everyone has its first choice
        for r in WEIRegistration.objects.filter(wei=self.wei).all():
            survey = WEISurvey2022(r)
            preferred_bus = survey.ordered_buses()[0][0]
            chosen_bus = survey.information.get_selected_bus()
            self.assertEqual(preferred_bus, chosen_bus)

    def test_survey_algorithm_full(self):
        """
        Buses are full of first year people, ensure that they are happy
        """
        # Add a lot of users
        for i in range(95):
            user = User.objects.create(username=f"user{i}")
            registration = WEIRegistration.objects.create(
                user=user,
                wei=self.wei,
                first_year=True,
                birth_date='2000-01-01',
            )
            information = WEISurveyInformation2022(registration)
            for j in range(1, 21):
                setattr(information, f'word{j}', random.choice(WORDS))
            information.step = 20
            information.save(registration)
            registration.save()

        # Run algorithm
        WEISurvey2022.get_algorithm_class()().run_algorithm()

        penalty = 0
        # Ensure that everyone seems to be happy
        # We attribute a penalty for each user that didn't have its first choice
        # The penalty is the square of the distance between the score of the preferred bus
        # and the score of the attributed bus
        # We consider it acceptable if the mean of this distance is lower than 5 %
        for r in WEIRegistration.objects.filter(wei=self.wei).all():
            survey = WEISurvey2022(r)
            chosen_bus = survey.information.get_selected_bus()
            buses = survey.ordered_buses()
            score = min(v for bus, v in buses if bus == chosen_bus)
            max_score = buses[0][1]
            penalty += (max_score - score) ** 2

            self.assertLessEqual(max_score - score, 25)  # Always less than 25 % of tolerance

        self.assertLessEqual(penalty / 100, 25)  # Tolerance of 5 %
