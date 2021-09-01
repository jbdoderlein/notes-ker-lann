import random

from django.contrib.auth.models import User
from django.test import TestCase

from wei.forms.surveys.wei2021 import WEIBusInformation2021, WEISurvey2021, WORDS, WEISurveyInformation2021
from wei.models import Bus, WEIClub, WEIRegistration


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
            name="WEI 2021",
            email="wei2021@example.com",
            date_start='2021-09-17',
            date_end='2021-09-19',
        )

        self.buses = []
        for i in range(10):
            bus = Bus.objects.create(wei=self.wei, name=f"Bus {i}", size=50)
            self.buses.append(bus)
            information = WEIBusInformation2021(bus)
            for word in WORDS:
                information.scores[word] = random.randint(0, 101)
            information.save()
            bus.save()

    def test_survey_algorithm_small(self):
        """
        There are only a few people in each bus, ensure that each person has its best bus
        """
        # Add a few users
        for i in range(50):
            user = User.objects.create(username=f"user{i}")
            registration = WEIRegistration.objects.create(
                user=user,
                wei=self.wei,
                first_year=True,
                birth_date='2000-01-01',
            )
            information = WEISurveyInformation2021(registration)
            for j in range(1, 21):
                setattr(information, f'word{j}', random.choice(WORDS))
            information.step = 20
            information.save(registration)
            registration.save()

        # Run algorithm
        WEISurvey2021.get_algorithm_class()().run_algorithm()

        # Ensure that everyone has its first choice
        for r in WEIRegistration.objects.filter(wei=self.wei).all():
            survey = WEISurvey2021(r)
            preferred_bus = survey.ordered_buses()[0][0]
            chosen_bus = survey.information.get_selected_bus()
            self.assertEqual(preferred_bus, chosen_bus)
