# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from member.models import Membership, Club
from permission.models import Role


class TestRightsPage(TestCase):
    """
    Display the rights page.
    """
    fixtures = ("initial",)

    def test_anonymous_rights_page(self):
        """
        Check that we can properly see the rights page even if we are not connected.
        We can't nethertheless see the club managers.
        """
        response = self.client.get(reverse("permission:rights"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse("special_memberships_table" in response.context)
        self.assertFalse("superusers" in response.context)

    def test_authenticated_rights_page(self):
        """
        Connect to the note and check that the club mangers are also displayed.
        """
        user = User.objects.create_superuser(
            username="ploptoto",
            password="totototo",
            email="toto@example.com",
        )
        self.client.force_login(user)
        membership = Membership.objects.create(user=user, club=Club.objects.get(name="BDE"))
        membership.roles.add(Role.objects.get(name="Respo info"))
        membership.save()

        response = self.client.get(reverse("permission:rights"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["special_memberships_table"])
        self.assertIsNotNone(response.context["superusers"])
