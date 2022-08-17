# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta, date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from activity.models import Activity
from member.models import Club, Membership
from note.models import NoteUser


class TestPermissionDenied(TestCase):
    """
    Load some protected pages and check that we have 403 errors.
    """
    fixtures = ('initial',)

    def setUp(self) -> None:
        # Create sample user with no rights
        self.user = User.objects.create(
            username="toto",
        )
        NoteUser.objects.create(user=self.user)
        self.client.force_login(self.user)

    def test_consos(self):
        response = self.client.get(reverse("note:consos"))
        self.assertEqual(response.status_code, 403)

    def test_create_activity(self):
        response = self.client.get(reverse("activity:activity_create"))
        self.assertEqual(response.status_code, 403)

    def test_activity_entries(self):
        activity = Activity.objects.create(
            name="",
            description="",
            creater=self.user,
            activity_type_id=1,
            organizer_id=1,
            attendees_club_id=1,
            date_start=timezone.now(),
            date_end=timezone.now(),
        )
        response = self.client.get(reverse("activity:activity_entry", kwargs=dict(pk=activity.pk)))
        self.assertEqual(response.status_code, 403)

    def test_invite_activity(self):
        activity = Activity.objects.create(
            name="",
            description="",
            creater=self.user,
            activity_type_id=1,
            organizer_id=1,
            attendees_club_id=1,
            date_start=timezone.now(),
            date_end=timezone.now(),
        )
        response = self.client.get(reverse("activity:activity_invite", kwargs=dict(pk=activity.pk)))
        self.assertEqual(response.status_code, 403)

    def test_create_club(self):
        response = self.client.get(reverse("member:club_create"))
        self.assertEqual(response.status_code, 403)

    def test_add_member_club(self):
        club = Club.objects.create(name=get_random_string(127))
        response = self.client.get(reverse("member:club_add_member", kwargs=dict(club_pk=club.pk)))
        self.assertEqual(response.status_code, 403)

    def test_renew_membership(self):
        club = Club.objects.create(name=get_random_string(127))
        membership = Membership.objects.create(user=self.user, club=club)
        response = self.client.get(reverse("member:club_renew_membership", kwargs=dict(pk=membership.pk)))
        self.assertEqual(response.status_code, 403)


    def test_create_invoice(self):
        response = self.client.get(reverse("treasury:invoice_create"))
        self.assertEqual(response.status_code, 403)

    def test_list_invoices(self):
        response = self.client.get(reverse("treasury:invoice_list"))
        self.assertEqual(response.status_code, 403)

    def test_create_remittance(self):
        response = self.client.get(reverse("treasury:remittance_create"))
        self.assertEqual(response.status_code, 403)

    def test_list_remittance(self):
        response = self.client.get(reverse("treasury:remittance_list"))
        self.assertEqual(response.status_code, 403)



class TestLoginRedirect(TestCase):
    def test_consos_page(self):
        response = self.client.get(reverse("note:consos"))
        self.assertRedirects(response, reverse("login") + "?next=" + reverse("note:consos"), 302, 200)
