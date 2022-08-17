# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date
from json.decoder import JSONDecodeError

from django.contrib.auth.models import User
from django.core.exceptions import FieldError
from django.db.models import F, Q
from django.test import TestCase
from django.utils import timezone
from member.models import Club, Membership
from note.models import NoteUser, Note, NoteClub, NoteSpecial


from ..models import Permission


class PermissionQueryTestCase(TestCase):
    fixtures = ('initial', )

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="user")
        NoteUser.objects.create(user=user)

    def test_permission_queries(self):
        """
        Check for all permissions that the query is compilable and that the database can parse the query.
        We use a random user.
        """
        for perm in Permission.objects.all():
            try:
                instanced = perm.about(
                    user=User.objects.get(),
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
                instanced.update_query()
                query = instanced.query
                model = perm.model.model_class()
                model.objects.filter(query).all()
            except (FieldError, AttributeError, ValueError, TypeError, JSONDecodeError):  # pragma: no cover
                print("Query error for permission", perm)
                print("Query:", perm.query)
                if instanced.query:
                    print("Compiled query:", instanced.query)
                raise
