# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import sys

from django.core.management import BaseCommand
from django.db import transaction

from ...forms import CurrentSurvey
from ...forms.surveys.wei2021 import WORDS   # WARNING: this is specific to 2021
from ...models import Bus


class Command(BaseCommand):
    """
    This script is used to load scores for buses from a CSV file.
    """
    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='Input CSV file')

    @transaction.atomic
    def handle(self, *args, **options):
        file = options['file']
        head = file.readline().replace('\n', '')
        bus_names = head.split(';')
        bus_names = [name for name in bus_names if name]
        buses = []
        for name in bus_names:
            qs = Bus.objects.filter(name__iexact=name)
            if not qs.exists():
                raise ValueError(f"Bus '{name}' does not exist")
            buses.append(qs.get())

        informations = {bus: CurrentSurvey.get_algorithm_class().get_bus_information(bus) for bus in buses}

        for line in file:
            elem = line.split(';')
            word = elem[0]
            if word not in WORDS:
                raise ValueError(f"Word {word} is not used")

            for i, bus in enumerate(buses):
                info = informations[bus]
                info.scores[word] = float(elem[i + 1].replace(',', '.'))

        for bus, info in informations.items():
            info.save()
            bus.save()
            if options['verbosity'] > 0:
                self.stdout.write(f"Bus {bus.name} saved!")
