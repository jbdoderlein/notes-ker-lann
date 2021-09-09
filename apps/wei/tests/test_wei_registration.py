# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from datetime import timedelta, date

from api.tests import TestAPI
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from member.models import Membership, Club
from note.models import NoteClub, SpecialTransaction, NoteUser
from treasury.models import SogeCredit

from ..api.views import BusViewSet, BusTeamViewSet, WEIClubViewSet, WEIMembershipViewSet, WEIRegistrationViewSet, \
    WEIRoleViewSet
from ..forms import CurrentSurvey, WEISurveyAlgorithm, WEISurvey
from ..models import WEIClub, Bus, BusTeam, WEIRole, WEIRegistration, WEIMembership


class TestWEIList(TestCase):
    fixtures = ('initial',)

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="weiadmin",
            password="admin",
            email="admin@example.com",
        )
        self.client.force_login(self.user)
        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

    def test_current_wei_detail(self):
        """
        Test that when no WEI is created, the WEI button redirect to the WEI list
        """
        response = self.client.get(reverse("wei:current_wei_detail"))
        self.assertRedirects(response, reverse("wei:wei_list"), 302, 200)


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
        self.user.save()
        self.client.force_login(self.user)
        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

        NoteUser.objects.create(user=self.user)

        self.year = timezone.now().year
        self.wei = WEIClub.objects.create(
            name="Test WEI",
            email="gc.wei@example.com",
            parent_club_id=2,
            membership_fee_paid=12500,
            membership_fee_unpaid=5500,
            membership_start=date(self.year, 1, 1),
            membership_end=date(self.year, 12, 31),
            year=self.year,
            date_start=date.today() + timedelta(days=2),
            date_end=date(self.year, 12, 31),
        )
        NoteClub.objects.create(club=self.wei)
        self.bus = Bus.objects.create(
            name="Test Bus",
            wei=self.wei,
            description="Test Bus",
        )

        # Setup the bus
        bus_info = CurrentSurvey.get_algorithm_class().get_bus_information(self.bus)
        bus_info.scores["Jus de fruit"] = 70
        bus_info.save()
        self.bus.save()

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
            birth_date=date(2000, 1, 1),
            gender="nonbinary",
            clothing_cut="male",
            clothing_size="XL",
            health_issues="I am a bot",
            emergency_contact_name="Pikachu",
            emergency_contact_phone="+33123456789",
            first_year=False,
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

        # Check that if the WEI is started, we can't update a wei
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:wei_update", kwargs=dict(pk=self.wei.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

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
        response = self.client.get(reverse("wei:add_bus", kwargs=dict(pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("wei:add_bus", kwargs=dict(pk=self.wei.pk)), dict(
            wei=self.wei.id,
            name="Create Bus Test",
            size=50,
            description="This bus was created.",
            information_json="{}",
        ))
        qs = Bus.objects.filter(name="Create Bus Test")
        self.assertTrue(qs.exists())
        bus = qs.get()
        CurrentSurvey.get_algorithm_class().get_bus_information(bus).save()
        self.assertRedirects(response, reverse("wei:manage_bus", kwargs=dict(pk=bus.pk)), 302, 200)

        # Check that if the WEI is started, we can't create a bus
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:add_bus", kwargs=dict(pk=self.wei.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

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
        response = self.client.get(reverse("wei:update_bus", kwargs=dict(pk=self.bus.pk)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("wei:update_bus", kwargs=dict(pk=self.bus.pk)), dict(
            name="Update Bus Test",
            size=40,
            description="This bus was updated.",
            information_json="{}",
        ))
        qs = Bus.objects.filter(name="Update Bus Test", id=self.bus.id)
        self.assertRedirects(response, reverse("wei:manage_bus", kwargs=dict(pk=self.bus.pk)), 302, 200)
        self.assertTrue(qs.exists())

        # Check that if the WEI is started, we can't update a bus
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:update_bus", kwargs=dict(pk=self.bus.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_add_team(self):
        """
        Test create a new team.
        """
        response = self.client.get(reverse("wei:add_team", kwargs=dict(pk=self.bus.pk)))
        self.assertEqual(response.status_code, 200)

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

        # Check that if the WEI is started, we can't create a team
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:add_team", kwargs=dict(pk=self.bus.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

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
        response = self.client.get(reverse("wei:update_bus_team", kwargs=dict(pk=self.team.pk)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("wei:update_bus_team", kwargs=dict(pk=self.team.pk)), dict(
            name="Update Team Test",
            color="#A6AA",
            description="This team was updated.",
        ))
        qs = BusTeam.objects.filter(name="Update Team Test", color=42666, id=self.team.id)
        self.assertRedirects(response, reverse("wei:manage_bus_team", kwargs=dict(pk=self.team.pk)), 302, 200)
        self.assertTrue(qs.exists())

        # Check that if the WEI is started, we can't update a team
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:update_bus_team", kwargs=dict(pk=self.team.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_register_2a(self):
        """
        Test register a new 2A+ to the WEI.
        """
        response = self.client.get(reverse("wei:wei_register_2A", kwargs=dict(wei_pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

        user = User.objects.create(username="toto", email="toto@example.com")

        # Try with an invalid form
        response = self.client.post(reverse("wei:wei_register_2A", kwargs=dict(wei_pk=self.wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date=date(2000, 1, 1),
            gender='nonbinary',
            clothing_cut='female',
            clothing_size='XS',
            health_issues='I am a bot',
            emergency_contact_name='NoteKfet2020',
            emergency_contact_phone='+33123456789',
            bus=[],
            team=[],
            roles=[],
        ))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["membership_form"].is_valid())

        response = self.client.post(reverse("wei:wei_register_2A", kwargs=dict(wei_pk=self.wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date=date(2000, 1, 1),
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

        # Check that the user can't be registered twice
        response = self.client.post(reverse("wei:wei_register_2A", kwargs=dict(wei_pk=self.wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date=date(2000, 1, 1),
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
        self.assertEqual(response.status_code, 200)
        self.assertTrue("This user is already registered to this WEI." in str(response.context["form"].errors))

        # Test the render of the page to register ourself if we have already opened a Société générale account
        SogeCredit.objects.create(user=self.user, credit_transaction=SpecialTransaction.objects.create(
            source_id=4,    # Bank transfer
            destination=self.user.note,
            quantity=1,
            amount=0,
            reason="Test",
            first_name="toto",
            last_name="toto",
            bank="Société générale",
        ))
        response = self.client.get(reverse("wei:wei_register_2A_myself", kwargs=dict(wei_pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

        # Check that if the WEI is started, we can't register anyone
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:wei_register_2A", kwargs=dict(wei_pk=self.wei.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_register_1a(self):
        """
        Test register a first year member to the WEI and complete the survey.
        """
        response = self.client.get(reverse("wei:wei_register_1A", kwargs=dict(wei_pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("wei:wei_register_1A_myself", kwargs=dict(wei_pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

        user = User.objects.create(username="toto", email="toto@example.com")
        response = self.client.post(reverse("wei:wei_register_1A", kwargs=dict(wei_pk=self.wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date=date(2000, 1, 1),
            gender='nonbinary',
            clothing_cut='female',
            clothing_size='XS',
            health_issues='I am a bot',
            emergency_contact_name='NoteKfet2020',
            emergency_contact_phone='+33123456789',
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
        survey.select_bus(self.bus)
        survey.save()
        self.assertIsNotNone(survey.information.get_selected_bus())

        # Check that the user can't be registered twice
        response = self.client.post(reverse("wei:wei_register_1A", kwargs=dict(wei_pk=self.wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date=date(2000, 1, 1),
            gender='nonbinary',
            clothing_cut='female',
            clothing_size='XS',
            health_issues='I am a bot',
            emergency_contact_name='NoteKfet2020',
            emergency_contact_phone='+33123456789',
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("This user is already registered to this WEI." in str(response.context["form"].errors))

        # Check that the user can't be registered twice as a first year member
        second_wei = WEIClub.objects.create(
            name="Second WEI",
            year=self.year + 1,
            date_start=str(self.year + 1) + "-01-01",
            date_end=str(self.year + 1) + "-12-31",
            membership_start=str(self.year) + "-01-01",
            membership_end=str(self.year + 1) + "-12-31",
        )
        response = self.client.post(reverse("wei:wei_register_1A", kwargs=dict(wei_pk=second_wei.pk)), dict(
            user=user.id,
            soge_credit=True,
            birth_date=date(2000, 1, 1),
            gender='nonbinary',
            clothing_cut='female',
            clothing_size='XS',
            health_issues='I am a bot',
            emergency_contact_name='NoteKfet2020',
            emergency_contact_phone='+33123456789',
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("This user can&#39;t be in her/his first year since he/she has already participated to a WEI."
                        in str(response.context["form"].errors))

        # Check that if the WEI is started, we can't register anyone
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:wei_register_1A", kwargs=dict(wei_pk=self.wei.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

        response = self.client.get(reverse("wei:wei_survey", kwargs=dict(pk=registration.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_wei_survey_ended(self):
        """
        Test display the end page of a survey.
        """
        response = self.client.get(reverse("wei:wei_survey_end", kwargs=dict(pk=self.registration.pk)))
        self.assertEqual(response.status_code, 200)

    def test_update_registration(self):
        """
        Test update a registration.
        """
        self.registration.information = dict(
            preferred_bus_pk=[],
            preferred_team_pk=[],
            preferred_roles_pk=[]
        )
        self.registration.save()

        response = self.client.get(reverse("wei:wei_update_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertEqual(response.status_code, 200)

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

        # Check the page when the registration is already validated
        membership = WEIMembership(
            user=self.user,
            club=self.wei,
            registration=self.registration,
            bus=self.bus,
            team=self.team,
        )
        membership._soge = True
        membership._force_renew_parent = True
        membership.save()
        soge_credit = SogeCredit.objects.get(user=self.user)
        soge_credit.credit_transaction = SpecialTransaction.objects.create(
            source_id=4,  # Bank transfer
            destination=self.user.note,
            quantity=1,
            amount=0,
            reason="Test",
            first_name="toto",
            last_name="toto",
            bank="Société générale",
        )
        soge_credit.save()

        sess = self.client.session
        sess["permission_mask"] = 0
        sess.save()
        response = self.client.get(reverse("wei:wei_update_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertEqual(response.status_code, 403)
        sess["permission_mask"] = 42
        sess.save()

        response = self.client.post(
            reverse("wei:wei_update_registration", kwargs=dict(pk=self.registration.pk)),
            dict(
                user=self.user.id,
                soge_credit=False,
                birth_date='2015-01-01',
                gender='male',
                clothing_cut='female',
                clothing_size='L',
                health_issues='I am really a bot',
                emergency_contact_name='Note Kfet 2020',
                emergency_contact_phone='+33600000000',
                bus=[self.bus.id],
                team=[self.team.id],
                roles=[role.id for role in WEIRole.objects.filter(name="Adhérent WEI").all()],
                information_json=self.registration.information_json,
            )
        )
        qs = WEIRegistration.objects.filter(user_id=self.user.id, clothing_size="L")
        self.assertTrue(qs.exists())
        self.assertRedirects(response, reverse("wei:validate_registration", kwargs=dict(pk=qs.get().pk)), 302, 200)

        # Test invalid form
        response = self.client.post(
            reverse("wei:wei_update_registration", kwargs=dict(pk=self.registration.pk)),
            dict(
                user=self.user.id,
                soge_credit=False,
                birth_date='2015-01-01',
                gender='male',
                clothing_cut='female',
                clothing_size='L',
                health_issues='I am really a bot',
                emergency_contact_name='Note Kfet 2020',
                emergency_contact_phone='+33600000000',
                bus=[],
                team=[],
                roles=[],
                information_json=self.registration.information_json,
            )
        )
        self.assertFalse(response.context["membership_form"].is_valid())

        # Check that if the WEI is started, we can't update a registration
        self.wei.date_start = date(2000, 1, 1)
        self.wei.update_membership_dates()
        self.wei.save()
        response = self.client.get(reverse("wei:wei_update_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_delete_registration(self):
        """
        Test delete a WEI registration.
        """
        response = self.client.get(reverse("wei:wei_delete_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(reverse("wei:wei_delete_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertRedirects(response, reverse("wei:wei_detail", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_validate_membership(self):
        """
        Test validate a membership.
        """
        response = self.client.get(reverse("wei:validate_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertEqual(response.status_code, 200)

        self.registration.first_year = True
        self.registration.save()

        response = self.client.get(reverse("wei:validate_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertEqual(response.status_code, 200)

        self.registration.first_year = False
        self.registration.save()

        # Check that a team must belong to the bus
        second_bus = Bus.objects.create(wei=self.wei, name="Second bus")
        second_team = BusTeam.objects.create(bus=second_bus, name="Second team", color=42)
        response = self.client.post(reverse("wei:validate_registration", kwargs=dict(pk=self.registration.pk)), dict(
            roles=[WEIRole.objects.get(name="GC WEI").id],
            bus=self.bus.pk,
            team=second_team.pk,
            credit_type=4,  # Bank transfer
            credit_amount=420,
            last_name="admin",
            first_name="admin",
            bank="Société générale",
        ))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertTrue("This team doesn&#39;t belong to the given bus." in str(response.context["form"].errors))

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

        # Check that if the WEI is started, we can't update a wei
        self.wei.date_start = date(2000, 1, 1)
        self.wei.save()
        response = self.client.get(reverse("wei:validate_registration", kwargs=dict(pk=self.registration.pk)))
        self.assertRedirects(response, reverse("wei:wei_closed", kwargs=dict(pk=self.wei.pk)), 302, 200)

    def test_registrations_list(self):
        """
        Test display the registration list, with or without a research
        """
        response = self.client.get(reverse("wei:wei_registrations", kwargs=dict(pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("wei:wei_registrations", kwargs=dict(pk=self.wei.pk)) + "?search=.")
        self.assertEqual(response.status_code, 200)

    def test_memberships_list(self):
        """
        Test display the memberships list, with or without a research
        """
        response = self.client.get(reverse("wei:wei_memberships", kwargs=dict(pk=self.wei.pk)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("wei:wei_memberships", kwargs=dict(pk=self.wei.pk)) + "?search=.")
        self.assertEqual(response.status_code, 200)

    def is_latex_installed(self):
        """
        Check if LaTeX is installed in the machine. Don't check pages that generate a PDF file if LaTeX is not
        installed, like in Gitlab.
        """
        with open("/dev/null", "wb") as devnull:
            return subprocess.call(
                ["/usr/bin/which", "xelatex"],
                stdout=devnull,
                stderr=devnull,
            ) == 0

    def test_memberships_pdf_list(self):
        """
        Test display the membership list as a PDF file
        """
        if self.is_latex_installed():
            response = self.client.get(reverse("wei:wei_memberships_pdf", kwargs=dict(wei_pk=self.wei.pk)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["content-type"], "application/pdf")

    def test_bus_memberships_pdf_list(self):
        """
        Test display the membership list of a bus as a PDF file
        """
        if self.is_latex_installed():
            response = self.client.get(reverse("wei:wei_memberships_bus_pdf", kwargs=dict(wei_pk=self.wei.pk,
                                                                                          bus_pk=self.bus.pk)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["content-type"], "application/pdf")

    def test_team_memberships_pdf_list(self):
        """
        Test display the membership list of a bus team as a PDF file
        """
        if self.is_latex_installed():
            response = self.client.get(reverse("wei:wei_memberships_team_pdf", kwargs=dict(wei_pk=self.wei.pk,
                                                                                           bus_pk=self.bus.pk,
                                                                                           team_pk=self.team.pk)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["content-type"], "application/pdf")


class TestDefaultWEISurvey(TestCase):
    """
    Doesn't test anything, just cover the default Survey classes.
    """
    def check_not_implemented(self, fun: callable, *args, **kwargs):
        self.assertRaises(NotImplementedError, fun, *args, **kwargs)

    def test_survey_classes(self):
        WEISurveyAlgorithm.get_bus_information_class()
        self.check_not_implemented(WEISurveyAlgorithm.get_survey_class)
        self.check_not_implemented(WEISurveyAlgorithm.get_registrations)
        self.check_not_implemented(WEISurveyAlgorithm.get_buses)
        self.check_not_implemented(WEISurveyAlgorithm().run_algorithm)

        self.check_not_implemented(WEISurvey, registration=None)
        self.check_not_implemented(WEISurvey.get_wei)
        self.check_not_implemented(WEISurvey.get_survey_information_class)
        self.check_not_implemented(WEISurvey.get_algorithm_class)
        self.check_not_implemented(WEISurvey.get_form_class, None)
        self.check_not_implemented(WEISurvey.form_valid, None, None)
        self.check_not_implemented(WEISurvey.is_complete, None)
        # noinspection PyTypeChecker
        WEISurvey.update_form(None, None)

        self.assertEqual(CurrentSurvey.get_algorithm_class().get_survey_class(), CurrentSurvey)
        self.assertEqual(CurrentSurvey.get_year(), 2021)


class TestWeiAPI(TestAPI):
    def setUp(self) -> None:
        super().setUp()

        self.year = timezone.now().year
        self.wei = WEIClub.objects.create(
            name="Test WEI",
            email="gc.wei@example.com",
            parent_club_id=2,
            membership_fee_paid=12500,
            membership_fee_unpaid=5500,
            membership_start=date(self.year, 1, 1),
            membership_end=date(self.year, 12, 31),
            membership_duration=396,
            year=self.year,
            date_start=date.today() + timedelta(days=2),
            date_end=date(self.year, 12, 31),
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
            birth_date=date(2000, 1, 1),
            gender="nonbinary",
            clothing_cut="male",
            clothing_size="XL",
            health_issues="I am a bot",
            emergency_contact_name="Pikachu",
            emergency_contact_phone="+33123456789",
            first_year=False,
        )
        Membership.objects.create(user=self.user, club=Club.objects.get(name="BDE"))
        Membership.objects.create(user=self.user, club=Club.objects.get(name="Kfet"))
        self.membership = WEIMembership.objects.create(
            user=self.user,
            club=self.wei,
            fee=125,
            bus=self.bus,
            team=self.team,
            registration=self.registration,
        )
        self.membership.roles.add(WEIRole.objects.last())
        self.membership.save()

    def test_weiclub_api(self):
        """
        Load WEI API page and test all filters and permissions
        """
        self.check_viewset(WEIClubViewSet, "/api/wei/club/")

    def test_wei_bus_api(self):
        """
        Load Bus API page and test all filters and permissions
        """
        self.check_viewset(BusViewSet, "/api/wei/bus/")

    def test_wei_team_api(self):
        """
        Load BusTeam API page and test all filters and permissions
        """
        self.check_viewset(BusTeamViewSet, "/api/wei/team/")

    def test_weirole_api(self):
        """
        Load WEIRole API page and test all filters and permissions
        """
        self.check_viewset(WEIRoleViewSet, "/api/wei/role/")

    def test_weiregistration_api(self):
        """
        Load WEIRegistration API page and test all filters and permissions
        """
        self.check_viewset(WEIRegistrationViewSet, "/api/wei/registration/")

    def test_weimembership_api(self):
        """
        Load WEIMembership API page and test all filters and permissions
        """
        self.check_viewset(WEIMembershipViewSet, "/api/wei/membership/")
