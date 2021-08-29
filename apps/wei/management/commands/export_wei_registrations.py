# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.management import BaseCommand, CommandError
from django.db.models import Q
from django.db.models.functions import Lower
from wei.models import WEIClub, Bus, BusTeam, WEIMembership


class Command(BaseCommand):
    help = "Export WEI registrations."

    def add_arguments(self, parser):
        parser.add_argument('--bus', '-b', choices=[bus.name for bus in Bus.objects.all()], type=str, default=None,
                            help='Filter by bus')
        parser.add_argument('--team', '-t', choices=[team.name for team in BusTeam.objects.all()], type=str,
                            default=None, help='Filter by team. Type "none" if you want to select the members '
                            + 'that are not in a team.')
        parser.add_argument('--year', '-y', type=int, default=None,
                            help='Select the year of the concerned WEI. Default: last year')
        parser.add_argument('--sep', type=str, default='|',
                            help='Select the CSV separator.')

    def handle(self, *args, **options):
        year = options["year"]
        if year:
            try:
                wei = WEIClub.objects.get(year=year)
            except WEIClub.DoesNotExist:
                raise CommandError("The WEI of year {:d} does not exist.".format(year,))
        else:
            wei = WEIClub.objects.order_by('-year').first()

        bus = options["bus"]
        if bus:
            try:
                bus = Bus.objects.filter(wei=wei).get(name=bus)
            except Bus.DoesNotExist:
                raise CommandError("The bus {} does not exist or does not belong to the WEI {}.".format(bus, wei.name,))

        team = options["team"]
        if team:
            if team.lower() == "none":
                team = 0
            else:
                try:
                    team = BusTeam.objects.filter(Q(bus=bus) | Q(wei=wei)).get(name=team)
                    bus = team.bus
                except BusTeam.DoesNotExist:
                    raise CommandError("The bus {} does not exist or does not belong to the bus {} neither the wei {}."
                                       .format(team, bus.name if bus else "<None>", wei.name,))

        qs = WEIMembership.objects
        qs = qs.filter(club=wei).order_by(
            Lower('bus__name'),
            Lower('team__name'),
            'user__profile__promotion',
            Lower('user__last_name'),
            Lower('user__first_name'),
        ).distinct()

        if bus:
            qs = qs.filter(bus=bus)

        if team is not None:
            qs = qs.filter(team=team if team else None)

        sep = options["sep"]

        self.stdout.write("Nom|Prénom|Date de naissance|Genre|Département|Année|Section|Bus|Équipe|Rôles"
                          .replace(sep, sep))

        for membership in qs.all():
            user = membership.user
            registration = membership.registration
            bus = membership.bus
            team = membership.team
            s = user.last_name
            s += sep + user.first_name
            s += sep + str(registration.birth_date)
            s += sep + registration.get_gender_display()
            s += sep + user.profile.get_department_display()
            s += sep + str(user.profile.ens_year) + "A"
            s += sep + user.profile.section_generated
            s += sep + bus.name
            s += sep + (team.name if team else "--")
            s += sep + ", ".join(role.name for role in membership.roles.filter(~Q(name="Adhérent WEI")).all())
            self.stdout.write(s)
