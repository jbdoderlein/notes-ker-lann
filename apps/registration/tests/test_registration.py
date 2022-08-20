# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from member.models import Club, Membership
from note.models import NoteUser, NoteSpecial, Transaction
from registration.tokens import email_validation_token

"""
Check that pre-registrations and validations are working as well.
"""


class TestSignup(TestCase):
    """
    Assume we are a new user.
    Check that it can pre-register without any problem.
    """

    fixtures = ("initial", )

    def test_signup(self):
        """
        A first year member signs up and validates its email address.
        """
        response = self.client.get(reverse("registration:signup"))
        self.assertEqual(response.status_code, 200)

        # Signup
        response = self.client.post(reverse("registration:signup"), dict(
            first_name="Toto",
            last_name="TOTO",
            username="toto",
            email="toto@example.com",
            password1="toto1234",
            password2="toto1234",
            phone_number="+33123456789",
            department="EXT",
            promotion=Club.objects.get(name="BDE").membership_start.year,
            address="Earth",
            paid=False,
            ml_events_registration="fr",
            ml_sport_registration=True,
            ml_art_registration=True,
        ))
        # Fail I don't know why ?
        self.assertRedirects(response, reverse("registration:email_validation_sent"), 302, 200)
        self.assertTrue(User.objects.filter(username="toto").exists())
        user = User.objects.get(username="toto")
        # A preregistred user has no note
        self.assertFalse(NoteUser.objects.filter(user=user).exists())
        self.assertFalse(user.profile.registration_valid)
        self.assertFalse(user.profile.email_confirmed)
        self.assertFalse(user.is_active)

        response = self.client.get(reverse("registration:email_validation_sent"))
        self.assertEqual(response.status_code, 200)

        # Check that the email validation link is valid
        token = email_validation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = self.client.get(reverse("registration:email_validation", kwargs=dict(uidb64=uid, token=token)))
        self.assertEqual(response.status_code, 200)
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.email_confirmed)

        # Token has expired
        response = self.client.get(reverse("registration:email_validation", kwargs=dict(uidb64=uid, token=token)))
        self.assertEqual(response.status_code, 400)

        # Uid does not exist
        response = self.client.get(reverse("registration:email_validation", kwargs=dict(uidb64=0, token="toto")))
        self.assertEqual(response.status_code, 400)

    def test_invalid_signup(self):
        """
        Send wrong data and check that it is not valid
        """
        User.objects.create_superuser(
            first_name="Toto",
            last_name="TOTO",
            username="toto",
            email="toto@example.com",
            password="toto1234",
        )

        # The email is already used
        response = self.client.post(reverse("registration:signup"), dict(
            first_name="Toto",
            last_name="TOTO",
            username="tôtö",
            email="toto@example.com",
            password1="toto1234",
            password2="toto1234",
            phone_number="+33123456789",
            department="EXT",
            promotion=Club.objects.get(name="BDE").membership_start.year,
            address="Earth",
            paid=False,
            ml_events_registration="en",
            ml_sport_registration=True,
            ml_art_registration=True,
        ))
        self.assertTrue(response.status_code, 200)

        # The username is similar to a known alias
        response = self.client.post(reverse("registration:signup"), dict(
            first_name="Toto",
            last_name="TOTO",
            username="tôtö",
            email="othertoto@example.com",
            password1="toto1234",
            password2="toto1234",
            phone_number="+33123456789",
            department="EXT",
            promotion=Club.objects.get(name="BDE").membership_start.year,
            address="Earth",
            paid=False,
            ml_events_registration="en",
            ml_sport_registration=True,
            ml_art_registration=True,
        ))
        self.assertTrue(response.status_code, 200)

        # The phone number is invalid
        response = self.client.post(reverse("registration:signup"), dict(
            first_name="Toto",
            last_name="TOTO",
            username="Ihaveanotherusername",
            email="othertoto@example.com",
            password1="toto1234",
            password2="toto1234",
            phone_number="invalid phone number",
            department="EXT",
            promotion=Club.objects.get(name="BDE").membership_start.year,
            address="Earth",
            paid=False,
            ml_events_registration="en",
            ml_sport_registration=True,
            ml_art_registration=True,
        ))
        self.assertTrue(response.status_code, 200)


class TestValidateRegistration(TestCase):
    """
    Test the admin interface to validate users
    """

    fixtures = ('initial',)

    def setUp(self) -> None:
        self.superuser = User.objects.create_superuser(
            username="admintoto",
            password="toto1234",
            email="admin.toto@example.com",
        )
        self.client.force_login(self.superuser)

        self.user = User.objects.create(
            username="toto",
            first_name="Toto",
            last_name="TOTO",
            email="toto@example.com",
        )

        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

    def test_future_user_list(self):
        """
        Display the list of pre-registered users
        """
        response = self.client.get(reverse("registration:future_user_list"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("registration:future_user_list") + "?search=toto")
        self.assertEqual(response.status_code, 200)

    def test_invalid_registrations(self):
        """
        Send wrong data and check that errors are detected
        """

        # The BDE membership is not free
        response = self.client.post(reverse("registration:future_user_detail", args=(self.user.pk,)), data=dict(
            credit_type=NoteSpecial.objects.get(special_type="Espèces").id,
            credit_amount=0,
            last_name="TOTO",
            first_name="Toto",
            join_bde=True,
            join_bda=False,
            join_bds=False
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

        # Last and first names are required for a credit
        response = self.client.post(reverse("registration:future_user_detail", args=(self.user.pk,)), data=dict(
            credit_type=NoteSpecial.objects.get(special_type="Chèque").id,
            credit_amount=4000,
            last_name="",
            first_name="",
            join_bde=True,
            join_bda=False,
            join_bds=False
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

        # The username admïntoto is too similar with the alias admintoto.
        # Since the form is valid, the user must update its username.
        self.user.username = "admïntoto"
        self.user.save()
        response = self.client.post(reverse("registration:future_user_detail", args=(self.user.pk,)), data=dict(
            credit_type=NoteSpecial.objects.get(special_type="Chèque").id,
            credit_amount=500,
            last_name="TOTO",
            first_name="Toto",
            join_bde=True,
            join_bda=False,
            join_bds=False
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_validate_bde_registration(self):
        """
        The user wants only to join the BDE. We validate the registration.
        """
        response = self.client.get(reverse("registration:future_user_detail", args=(self.user.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.user.profile.get_absolute_url())
        self.assertEqual(response.status_code, 404)

        self.user.profile.email_confirmed = True
        self.user.profile.save()

        response = self.client.post(reverse("registration:future_user_detail", args=(self.user.pk,)), data=dict(
            credit_type=NoteSpecial.objects.get(special_type="Chèque").id,
            credit_amount=500,
            last_name="TOTO",
            first_name="Toto",
            join_bde=True,
            join_bda=False,
            join_bds=True
        ))
        self.assertRedirects(response, self.user.profile.get_absolute_url(), 302, 200)
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.registration_valid)
        self.assertTrue(NoteUser.objects.filter(user=self.user).exists())
        self.assertTrue(Membership.objects.filter(club__name="BDE", user=self.user).exists())
        self.assertFalse(Membership.objects.filter(club__name="BDA", user=self.user).exists())
        self.assertTrue(Membership.objects.filter(club__name="BDS", user=self.user).exists())
        self.assertEqual(Transaction.objects.filter(
            Q(source=self.user.note) | Q(destination=self.user.note)).count(), 3)

        response = self.client.get(self.user.profile.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_validate_kfet_registration(self):
        """
        The user joins the BDE,BDA and BDS.
        """
        response = self.client.get(reverse("registration:future_user_detail", args=(self.user.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.user.profile.get_absolute_url())
        self.assertEqual(response.status_code, 404)

        self.user.profile.email_confirmed = True
        self.user.profile.save()

        response = self.client.post(reverse("registration:future_user_detail", args=(self.user.pk,)), data=dict(
            credit_type=NoteSpecial.objects.get(special_type="Espèces").id,
            credit_amount=4000,
            last_name="TOTO",
            first_name="Toto",
            join_bde=True,
            join_bda=True,
            join_bds=True
        ))
        self.assertRedirects(response, self.user.profile.get_absolute_url(), 302, 200)
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.registration_valid)
        self.assertTrue(NoteUser.objects.filter(user=self.user).exists())
        self.assertTrue(Membership.objects.filter(club__name="BDE", user=self.user).exists())
        self.assertTrue(Membership.objects.filter(club__name="BDA", user=self.user).exists())
        self.assertTrue(Membership.objects.filter(club__name="BDS", user=self.user).exists())
        self.assertEqual(Transaction.objects.filter(
            Q(source=self.user.note) | Q(destination=self.user.note)).count(), 4)

        response = self.client.get(self.user.profile.get_absolute_url())
        self.assertEqual(response.status_code, 200)


    def test_invalidate_registration(self):
        """
        Try to invalidate (= delete) pre-registration.
        """
        response = self.client.get(reverse("registration:future_user_invalidate", args=(self.user.pk,)))
        self.assertRedirects(response, reverse("registration:future_user_list"), 302, 200)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_resend_email_validation_link(self):
        """
        Resend email validation linK.
        """
        response = self.client.get(reverse("registration:email_validation_resend", args=(self.user.pk,)))
        self.assertRedirects(response, reverse("registration:future_user_detail", args=(self.user.pk,)), 302, 200)
