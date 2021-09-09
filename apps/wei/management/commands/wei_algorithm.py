# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from argparse import ArgumentParser, FileType

from django.core.management import BaseCommand
from django.db import transaction

from ...forms import CurrentSurvey


class Command(BaseCommand):
    help = "Attribute to each first year member a bus for the WEI"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--doit', '-d', action='store_true', help='Finally run the algorithm in non-dry mode.')
        parser.add_argument('--output', '-o', nargs='?', type=FileType('w'), default=self.stdout,
                            help='Output file for the algorithm result. Default is standard output.')

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Run the WEI algorithm to attribute a bus to each first year member.
        """
        sid = transaction.savepoint()

        algorithm = CurrentSurvey.get_algorithm_class()()
        algorithm.run_algorithm()

        output = options['output']
        registrations = algorithm.get_registrations()
        per_bus = {bus: [r for r in registrations if 'selected_bus_pk' in r.information
                         and r.information['selected_bus_pk'] == bus.pk]
                   for bus in algorithm.get_buses()}
        for bus, members in per_bus.items():
            output.write(bus.name + "\n")
            output.write("=" * len(bus.name) + "\n")
            for r in members:
                output.write(r.user.username + "\n")
            output.write("\n")

        if not options['doit']:
            self.stderr.write(self.style.WARNING("Running in dry mode. "
                                                 "Use --doit option to really execute the algorithm."))
            transaction.savepoint_rollback(sid)
            return
