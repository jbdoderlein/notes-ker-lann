# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from member.models import Membership
from note.models import NoteClub

from ..forms import CurrentSurvey
from ..models import WEIClub, Bus, BusTeam, WEIRole, WEIRegistration, WEIMembership


class TestWEIRegistration(TestCase):
    """
    Test the whole WEI app
    """
    fixtures = ('initial',)

    def setUp(self):
        """
        Setup the database with initial data
        Create a new user, a new WEI, bus, team, registration
        """
        self.user = User.objects.create_superuser(
            username="weiadmin",
            password="admin",
            email="admin@example.com",
        )
        self.client.force_login(self.user)
        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

        self.year = timezone.now().year
        self.wei = WEIClub.objects.create(
            name="Test WEI",
            email="gc.wei@example.com",
            parent_club_id=2,
            membership_fee_paid=12500,
            membership_fee_unpaid=5500,
            membership_start=str(self.year) + "-08-01",
            membership_end=str(self.year) + "-12-31",
            year=self.year,
            date_start=str(self.year) + "-09-01",
            date_end=str(self.year) + "-09-03",
        )
        NoteClub.objects.create(club=self.wei)
        self.bus = Bus.objects.create(
            name="Test Bus",
            wei=self.wei,
            description="Test Bus",
        )
        self.team = BusTeam.objects.create(
            name="Test Team",
            bus=self.bus,
            color=0xFFFFFF,
            description="Test Team",
        )
        self.registration = WEIRegistration.objects.create(
            user_id=self.user.id,
            wei_id=self.wei.id,
            soge_credit=True,
            caution_check=True,
            birth_date="2000-01-01",
            gender="nonbinary",
            clothing_cut="male",
            clothing_size="XL",
            health_issues="I am a bot",
            emergency_contact_name="Pikachu",
            emergency_contact_phone="+33123456789",
            ml_events_registration=True,
            ml_sport_registration=True,
            ml_art_registration=True,
            first_year=True,
        )

    def test_create_wei(self):
        """
        Test creating a new WEI club.
        """
        response = self.client.post(reverse("wei:wei_create"), dict(
            name="Create WEI Test",
            email="gc.wei@example.com",
            membership_fee_paid=12500,
            membership_fee_unpaid=5500,
            membership_start=str(self.year + 1) + "-08-01",
            membership_end=str(self.year + 1) + "-09-30",
            year=self.year + 1,
            date_start=str(self.year + 1) + "-09-01",
            date_end=str(self.year + 1) + "-09-03",
        ))
        qs = WEIClub.objects.filter(name="Create WEI Test", year=self.year + 1)
        self.assertTrue(qs.exists())
        wei = qs.get()
        self.assertRedirects(response, reverse("wei:wei_detail", kwargs=dict(pk=wei.pk)), 302, 200)

    def test_wei_detail(self):
        """
        Test display the information about the default WEI.
        """
        response = self.client.get(reverse("wei:wei_detail", kwargs=dict(pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

    def test_current_wei_detail(self):
        """
        Test display the information about the current WEI.
        """
        response = self.client.get(reverse("wei:current_wei_detail"))
        self.assertRedirects(response, reverse("wei:wei_detail", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_update_wei(self):
        """
        Test update the information about the default WEI.
        """
        response = self.client.post(reverse("wei:wei_update", kwargs=dict(pk=self.wei.pk)), dict(
            name="Update WEI Test",
            year=2000,
            email="wei-updated@example.com",
            membership_fee_paid=0,
            membership_fee_unpaid=0,
            membership_start="2000-08-01",
            membership_end="2000-09-30",
            date_start="2000-09-01",
            date_end="2000-09-03",
        ))
        qs = WEIClub.objects.filter(name="Update WEI Test", id=self.wei.id)
        self.assertRedirects(response, reverse("wei:wei_detail", kwargs=dict(pk=self.wei.pk)), 302, 200)
        self.assertTrue(qs.exists())

    def test_wei_closed(self):
        """
        Test display the page when a WEI is closed.
        """
        response = self.client.get(reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

    def test_wei_list(self):
        """
        Test display the list of all WEI.
        """
        response = self.client.get(reverse("wei:wei_list"))
        self.assertEqual(response.status_code, 200)

    def test_add_bus(self):
        """
        Test create a new bus.
        """
        response = self.client.post(reverse("wei:add_bus", kwargs=dict(pk=self.wei.pk)), dict(
            wei=self.wei.id,
            name="Create Bus Test",
            description="This bus was created.",
        ))
        qs = Bus.objects.filter(name="Create Bus Test")
        self.assertTrue(qs.exists())
        bus = qs.get()
        self.assertRedirects(response, reverse("wei:manage_bus", kwargs=dict(pk=bus.pk)), 302, 200)

    def test_detail_bus(self):
        """
        Test display the information about a bus.
        """
        response = self.client.get(reverse("wei:manage_bus", kwargs=dict(pk=self.bus.pk)))
        self.assertEqual(response.status_code, 200)

    def test_update_bus(self):
        """
        Test update a bus.
        """
        response = self.client.post(reverse("wei:update_bus", kwargs=dict(pk=self.bus.pk)), dict(
            name="Update Bus Test",
            description="This bus was updated.",
        ))
        qs = Bus.objects.filter(name="Update Bus Test", id=self.bus.id)
        self.assertRedirects(response, reverse("wei:manage_bus", kwargs=dict(pk=self.bus.pk)), 302, 200)
        self.assertTrue(qs.exists())

    def test_add_team(self):
        """
        Test create a new team.
        """
        response = self.client.post(reverse("wei:add_team", kwargs=dict(pk=self.bus.pk)), dict(
            bus=self.bus.id,
            name="Create Team Test",
            color="#2A",
            description="This team was created.",
        ))
        qs = BusTeam.objects.filter(name="Create Team Test", color=42)
        self.assertTrue(qs.exists())
        team = qs.get()
        self.assertRedirects(response, reverse("wei:manage_bus_team", kwargs=dict(pk=team.pk)), 302, 200)

    def test_detail_team(self):
        """
        Test display the detail about a team.
        """
        response = self.client.get(reverse("wei:manage_bus_team", kwargs=dict(pk=self.team.pk)))
        self.assertEqual(response.status_code, 200)

    def test_update_team(self):
        """
        Test update a team.
        """
        response = self.client.post(reverse("wei:update_bus_team", kwargs=dict(pk=self.team.pk)), dict(
            name="Update Team Test",
            color="#A6AA",
            description="This team was updated.",
        ))
        qs = BusTeam.objects.filter(name="Update Team Test", color=42666, id=self.team.id)
        self.assertRedirects(response, reverse("wei:manage_bus_team", kwargs=dict(pk=self.team.pk)), 302, 200)
        self.assertTrue(qs.exists())

    def test_register_2a(self):
        """
        Test register a new 2A+ to the WEI.
        """
        user = User.objects.create(username="toto", email="toto@example.com")
        response = self.client.post(reverse("wei:wei_register_2A", kwargs=dict(wei_pk=self.wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date='2000-01-01',
            gender='nonbinary',
            clothing_cut='female',
            clothing_size='XS',
            health_issues='I am a bot',
            emergency_contact_name='NoteKfet2020',
            emergency_contact_phone='+33123456789',
            bus=[self.bus.id],
            team=[self.team.id],
            roles=[role.id for role in WEIRole.objects.filter(~Q(name="1A")).all()],
        ))
        qs = WEIRegistration.objects.filter(user_id=user.id)
        self.assertTrue(qs.exists())
        self.assertRedirects(response, reverse("wei:wei_survey", kwargs=dict(pk=qs.get().pk)), 302, 302)

    def test_register_1a(self):
        """
        Test register a first year member to the WEI and complete the survey.
        """
        user = User.objects.create(username="toto", email="toto@example.com")
        response = self.client.post(reverse("wei:wei_register_1A_myself", kwargs=dict(wei_pk=self.wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date='2000-01-01',
            gender='nonbinary',
            clothing_cut='female',
            clothing_size='XS',
            health_issues='I am a bot',
            emergency_contact_name='NoteKfet2020',
            emergency_contact_phone='+33123456789',
            ml_events_registration=True,
            ml_sport_registration=False,
            ml_art_registration=False,
        ))
        qs = WEIRegistration.objects.filter(user_id=user.id)
        self.assertTrue(qs.exists())
        registration = qs.get()
        self.assertRedirects(response, reverse("wei:wei_survey", kwargs=dict(pk=registration.pk)), 302, 200)
        for i in range(1, 21):
            # Fill 1A Survey, 20 pages
            response = self.client.post(reverse("wei:wei_survey", kwargs=dict(pk=registration.pk)), dict(
                word="Jus de fruit",
            ))
            registration.refresh_from_db()
            survey = CurrentSurvey(registration)
            self.assertRedirects(response, reverse("wei:wei_survey", kwargs=dict(pk=registration.pk)), 302,
                                 302 if survey.is_complete() else 200)
            self.assertIsNotNone(getattr(survey.information, "word" + str(i)), "Survey page #" + str(i) + " failed")
        survey = CurrentSurvey(registration)
        self.assertTrue(survey.is_complete())

    def test_wei_survey_ended(self):
        """
        Test display the end page of a survey.
        """
        response = self.client.get(reverse("wei:wei_survey_end", kwargs=dict(pk=self.registration.pk)))
        self.assertEqual(response.status_code, 200)

    def test_update_registration(self):
        self.registration.information = dict(
            preferred_bus_pk=[],
            preferred_team_pk=[],
            preferred_roles_pk=[]
        )
        self.registration.save()

        response = self.client.post(
            reverse("wei:wei_update_registration", kwargs=dict(pk=self.registration.pk)),
            dict(
                user=self.user.id,
                soge_credit=False,
                birth_date='2020-01-01',
                gender='female',
                clothing_cut='male',
                clothing_size='M',
                health_issues='I am really a bot',
                emergency_contact_name='Note Kfet 2020',
                emergency_contact_phone='+33600000000',
                bus=[self.bus.id],
                team=[self.team.id],
                roles=[role.id for role in WEIRole.objects.filter(name="Adhérent WEI").all()],
                information_json=self.registration.information_json,
            )
        )
        qs = WEIRegistration.objects.filter(user_id=self.user.id, soge_credit=False, clothing_size="M")
        self.assertTrue(qs.exists())
        self.assertRedirects(response, reverse("wei:validate_registration", kwargs=dict(pk=qs.get().pk)), 302, 200)

    def test_delete_registration(self):
        """
        Test delete a WEI registration.
        """
        response = self.client.delete(reverse("wei:wei_delete_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertRedirects(response, reverse("wei:wei_detail", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_validate_membership(self):
        """
        Test validate a membership.
        """
        response = self.client.post(reverse("wei:validate_registration", kwargs=dict(pk=self.registration.pk)), dict(
            roles=[WEIRole.objects.get(name="GC WEI").id],
            bus=self.bus.pk,
            team=self.team.pk,
            credit_type=4,  # Bank transfer
            credit_amount=420,
            last_name="admin",
            first_name="admin",
            bank="Société générale",
        ))
        self.assertRedirects(response, reverse("wei:wei_detail", kwargs=dict(pk=self.registration.wei.pk)), 302, 200)
        # Check if the membership is successfully created
        membership = WEIMembership.objects.filter(user_id=self.user.id, club=self.wei)
        self.assertTrue(membership.exists())
        membership = membership.get()
        # Check if the user is member of the Kfet club and the BDE
        kfet_membership = Membership.objects.filter(user_id=self.user.id, club__name="Kfet")
        self.assertTrue(kfet_membership.exists())
        kfet_membership = kfet_membership.get()
        bde_membership = Membership.objects.filter(user_id=self.user.id, club__name="BDE")
        self.assertTrue(bde_membership.exists())
        bde_membership = bde_membership.get()

        if "treasury" in settings.INSTALLED_APPS:
            # The registration is made with the Société générale. Ensure that all is fine
            from treasury.models import SogeCredit
            soge_credit = SogeCredit.objects.filter(user_id=self.user.id)
            self.assertTrue(soge_credit.exists())
            soge_credit = soge_credit.get()
            self.assertTrue(membership.transaction in soge_credit.transactions.all())
            self.assertTrue(kfet_membership.transaction in soge_credit.transactions.all())
            self.assertTrue(bde_membership.transaction in soge_credit.transactions.all())
            self.assertFalse(membership.transaction.valid)
            self.assertFalse(kfet_membership.transaction.valid)
            self.assertFalse(bde_membership.transaction.valid)

    def test_registrations_list(self):
        """
        Test display the registration list
        """
        response = self.client.get(reverse("wei:wei_registrations", kwargs=dict(pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

    def test_memberships_list(self):
        """
        Test display the memberships list
        """
        response = self.client.get(reverse("wei:wei_memberships", kwargs=dict(pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

    def test_memberships_pdf_list(self):
        """
        Test display the membership list as a PDF file
        """
        response = self.client.get(reverse("wei:wei_memberships_pdf", kwargs=dict(wei_pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/pdf")

    def test_bus_memberships_pdf_list(self):
        """
        Test display the membership list of a bus as a PDF file
        """
        response = self.client.get(reverse("wei:wei_memberships_bus_pdf", kwargs=dict(wei_pk=self.wei.pk,
                                                                                      bus_pk=self.bus.pk)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/pdf")

    def test_team_memberships_pdf_list(self):
        """
        Test display the membership list of a bus team as a PDF file
        """
        response = self.client.get(reverse("wei:wei_memberships_team_pdf", kwargs=dict(wei_pk=self.wei.pk,
                                                                                       bus_pk=self.bus.pk,
                                                                                       team_pk=self.team.pk)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/pdf")
