# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from activity.models import Activity, ActivityType, Guest, Entry
from member.models import Club


class TestActivities(TestCase):
    """
    Test activities
    """
    fixtures = ('initial',)

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admintoto",
            password="tototototo",
            email="toto@example.com"
        )
        self.client.force_login(self.user)

        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

        self.activity = Activity.objects.create(
            name="Activity",
            description="This is a test activity\non two very very long lines\nbecause this is very important.",
            location="Earth",
            activity_type=ActivityType.objects.get(name="Pot"),
            creater=self.user,
            organizer=Club.objects.get(name="Kfet"),
            attendees_club=Club.objects.get(name="Kfet"),
            date_start=timezone.now(),
            date_end=timezone.now() + timedelta(days=2),
            valid=True,
        )

        self.guest = Guest.objects.create(
            activity=self.activity,
            inviter=self.user.note,
            last_name="GUEST",
            first_name="Guest",
        )

    def test_activity_list(self):
        """
        Display the list of all activities
        """
        response = self.client.get(reverse("activity:activity_list"))
        self.assertEqual(response.status_code, 200)

    def test_activity_create(self):
        """
        Create a new activity
        """
        response = self.client.get(reverse("activity:activity_create"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("activity:activity_create"), data=dict(
            name="Activity created",
            description="This activity was successfully created.",
            location="Earth",
            activity_type=ActivityType.objects.get(name="Soirée de club").id,
            creater=self.user.id,
            organizer=Club.objects.get(name="Kfet").id,
            attendees_club=Club.objects.get(name="Kfet").id,
            date_start="{:%Y-%m-%d %H:%M}".format(timezone.now()),
            date_end="{:%Y-%m-%d %H:%M}".format(timezone.now() + timedelta(days=2)),
            valid=True,
        ))
        self.assertTrue(Activity.objects.filter(name="Activity created").exists())
        activity = Activity.objects.get(name="Activity created")
        self.assertRedirects(response, reverse("activity:activity_detail", args=(activity.pk,)), 302, 200)

    def test_activity_detail(self):
        """
        Display the detail of an activity
        """
        response = self.client.get(reverse("activity:activity_detail", args=(self.activity.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_activity_update(self):
        """
        Update an activity
        """
        response = self.client.get(reverse("activity:activity_update", args=(self.activity.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("activity:activity_update", args=(self.activity.pk,)), data=dict(
            name=str(self.activity) + " updated",
            description="This activity was successfully updated.",
            location="Earth",
            activity_type=ActivityType.objects.get(name="Autre").id,
            creater=self.user.id,
            organizer=Club.objects.get(name="Kfet").id,
            attendees_club=Club.objects.get(name="Kfet").id,
            date_start="{:%Y-%m-%d %H:%M}".format(timezone.now()),
            date_end="{:%Y-%m-%d %H:%M}".format(timezone.now() + timedelta(days=2)),
            valid=True,
        ))
        self.assertTrue(Activity.objects.filter(name="Activity updated").exists())
        self.assertRedirects(response, reverse("activity:activity_detail", args=(self.activity.pk,)), 302, 200)

    def test_activity_entry(self):
        """
        Create some entries
        """
        self.activity.open = True
        self.activity.save()

        response = self.client.get(reverse("activity:activity_entry", args=(self.activity.pk,)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("activity:activity_entry", args=(self.activity.pk,)) + "?search=guest")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("activity:activity_entry", args=(self.activity.pk,)) + "?search=admin")
        self.assertEqual(response.status_code, 200)

        # User entry
        response = self.client.post("/api/activity/entry/", data=dict(
            activity=self.activity.id,
            note=self.user.note.id,
            guest="",
        ))
        self.assertEqual(response.status_code, 201)     # 201 = Created
        self.assertTrue(Entry.objects.filter(note=self.user.note, guest=None, activity=self.activity).exists())

        # Guest entry
        response = self.client.post("/api/activity/entry/", data=dict(
            activity=self.activity.id,
            note=self.user.note.id,
            guest=self.guest.id,
        ))
        self.assertEqual(response.status_code, 201)     # 201 = Created
        self.assertTrue(Entry.objects.filter(note=self.user.note, guest=self.guest.id, activity=self.activity).exists())

    def test_activity_invite(self):
        """
        Try to invite people to an activity
        """
        response = self.client.get(reverse("activity:activity_invite", args=(self.activity.pk,)))
        self.assertEqual(response.status_code, 200)

        # The activity is started, can't invite
        response = self.client.post(reverse("activity:activity_invite", args=(self.activity.pk,)), data=dict(
            activity=self.activity.id,
            inviter=self.user.note.id,
            last_name="GUEST2",
            first_name="Guest",
        ))
        self.assertEqual(response.status_code, 200)

        self.activity.date_start += timedelta(days=1)
        self.activity.save()

        response = self.client.post(reverse("activity:activity_invite", args=(self.activity.pk,)), data=dict(
            activity=self.activity.id,
            inviter=self.user.note.id,
            last_name="GUEST2",
            first_name="Guest",
        ))
        self.assertRedirects(response, reverse("activity:activity_detail", args=(self.activity.pk,)), 302, 200)

    def test_activity_ics(self):
        """
        Render the ICS calendar
        """
        response = self.client.get(reverse("activity:calendar_ics"))
        self.assertEqual(response.status_code, 200)
