# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _

from wei.forms import CurrentSurvey


class Command(BaseCommand):
    help = _("Attribute to each first year member a bus for the WEI")

    def handle(self, *args, **options):
        CurrentSurvey.get_algorithm_class()().run_algorithm()
