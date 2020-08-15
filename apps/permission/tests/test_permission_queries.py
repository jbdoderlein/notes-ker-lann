# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import FieldError
from django.db.models import F, Q
from django.test import TestCase
from django.utils import timezone
from member.models import Club, Membership
from note.models import NoteUser, Note, NoteClub, NoteSpecial
from wei.models import WEIMembership, WEIRegistration, WEIClub, Bus, BusTeam

from ..models import Permission


class PermissionQueryTestCase(TestCase):
    fixtures = ('initial', )

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="user")
        NoteUser.objects.create(user=user)
        wei = WEIClub.objects.create(
            name="wei",
            date_start=date.today(),
            date_end=date.today(),
        )
        NoteClub.objects.create(club=wei)
        weiregistration = WEIRegistration.objects.create(
            user=user,
            wei=wei,
            birth_date=date.today(),
        )
        bus = Bus.objects.create(
            name="bus",
            wei=wei,
        )
        team = BusTeam.objects.create(
            name="team",
            bus=bus,
            color=0xFFFFFF,
        )
        WEIMembership.objects.create(
            user=user,
            club=wei,
            registration=weiregistration,
            bus=bus,
            team=team,
        )

    def test_permission_queries(self):
        """
        Check for all permissions that the query is compilable and that the database can parse the query.
        We use a random user with a random WEIClub (to use permissions for the WEI) in a random team in a random bus.
        """
        for perm in Permission.objects.all():
            instanced = perm.about(
                user=User.objects.get(),
                club=WEIClub.objects.get(),
                membership=Membership.objects.get(),
                User=User,
                Club=Club,
                Membership=Membership,
                Note=Note,
                NoteUser=NoteUser,
                NoteClub=NoteClub,
                NoteSpecial=NoteSpecial,
                F=F,
                Q=Q,
                now=timezone.now(),
                today=date.today(),
            )
            try:
                instanced.update_query()
                query = instanced.query
                model = perm.model.model_class()
                model.objects.filter(query).all()
                # print("Good query for permission", perm)
            except (FieldError, AttributeError, ValueError, TypeError):
                print("Query error for permission", perm)
                print("Query:", perm.query)
                if instanced.query:
                    print("Compiled query:", instanced.query)
                raise
