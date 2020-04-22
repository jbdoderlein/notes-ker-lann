# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.management import BaseCommand

from ...forms import CurrentSurvey


class Command(BaseCommand):
    help = "Attribute to each first year member a bus for the WEI"

    def handle(self, *args, **options):
        """
        Run the WEI algorithm to attribute a bus to each first year member.
        """
        CurrentSurvey.get_algorithm_class()().run_algorithm()
