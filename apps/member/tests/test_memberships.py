# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import hashlib
import os
from datetime import date, timedelta

from api.tests import TestAPI
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from note.models import Alias, NoteSpecial
from permission.models import Role
from treasury.models import SogeCredit

from ..api.views import ClubViewSet, MembershipViewSet, ProfileViewSet
from ..models import Club, Membership, Profile

"""
Create some users and clubs and test that all pages are rendering properly
and that memberships are working.
"""


class TestMemberships(TestCase):
    fixtures = ('initial', )

    def setUp(self) -> None:
        """
        Create a sample superuser, a club and a membership for all tests.
        """
        self.user = User.objects.create_superuser(
            username="toto",
            email="toto@example.com",
            password="toto",
        )
        self.user.profile.registration_valid = True
        self.user.profile.email_confirmed = True
        self.user.profile.save()
        self.client.force_login(self.user)

        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

        self.club = Club.objects.create(name="totoclub", parent_club=Club.objects.get(name="BDE"))
        self.bde_membership = Membership.objects.create(user=self.user, club=Club.objects.get(name="BDE"))
        self.membership = Membership.objects.create(user=self.user, club=self.club)
        self.membership.roles.add(Role.objects.get(name="Bureau de club"))
        self.membership.save()

    def test_admin_pages(self):
        """
        Check that Django Admin pages for the member app are loading successfully.
        """
        response = self.client.get(reverse("admin:index") + "member/membership/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "member/club/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "auth/user/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "auth/user/" + str(self.user.pk) + "/change/")
        self.assertEqual(response.status_code, 200)

    def test_render_club_list(self):
        """
        Render the list of all clubs, with a search.
        """
        response = self.client.get(reverse("member:club_list"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("member:club_list") + "?search=toto")
        self.assertEqual(response.status_code, 200)

    def test_render_club_create(self):
        """
        Try to create a new club.
        """
        response = self.client.get(reverse("member:club_create"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("member:club_create"), data=dict(
            name="Club toto",
            email="clubtoto@example.com",
            parent_club=self.club.pk,
            require_memberships=False,
            membership_fee_paid=0,
            membership_fee_unpaid=0,
        ))
        self.assertTrue(Club.objects.filter(name="Club toto").exists())
        club = Club.objects.get(name="Club toto")
        self.assertRedirects(response, club.get_absolute_url(), 302, 200)

    def test_render_club_detail(self):
        """
        Display the detail of a club.
        """
        response = self.client.get(reverse("member:club_detail", args=(self.club.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_render_club_update(self):
        """
        Try to update the information about a club.
        """
        response = self.client.get(reverse("member:club_update", args=(self.club.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("member:club_update", args=(self.club.pk, )), data=dict(
            name="Toto club updated",
            email="clubtoto@example.com",
            require_memberships=True,
            membership_fee_paid=0,
            membership_fee_unpaid=0,
        ))
        self.assertRedirects(response, self.club.get_absolute_url(), 302, 200)
        self.assertTrue(Club.objects.exclude(name="Toto club updated"))

    def test_render_club_update_picture(self):
        """
        Try to update the picture of the note of a club.
        """
        response = self.client.get(reverse("member:club_update_pic", args=(self.club.pk,)))
        self.assertEqual(response.status_code, 200)

        old_pic = self.club.note.display_image

        with open("apps/member/static/member/img/default_picture.png", "rb") as f:
            image = SimpleUploadedFile("image.png", f.read(), "image/png")
            response = self.client.post(reverse("member:club_update_pic", args=(self.club.pk,)), dict(
                image=image,
                x=0,
                y=0,
                width=200,
                height=200,
            ))
            self.assertRedirects(response, self.club.get_absolute_url(), 302, 200)

        self.club.note.refresh_from_db()
        self.assertTrue(os.path.exists(self.club.note.display_image.path))
        os.remove(self.club.note.display_image.path)

        self.club.note.display_image = old_pic
        self.club.note.save()

    def test_render_club_aliases(self):
        """
        Display the list of the aliases of a club.
        """
        # Alias creation and deletion is already tested in the note app
        response = self.client.get(reverse("member:club_alias", args=(self.club.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_render_club_members(self):
        """
        Display the list of the members of a club.
        """
        response = self.client.get(reverse("member:club_members", args=(self.club.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("member:club_members", args=(self.club.pk,)) + "?search=toto&roles="
                                   + ",".join([str(role.pk) for role in
                                               Role.objects.filter(weirole__isnull=True).all()]))
        self.assertEqual(response.status_code, 200)

    def test_render_club_add_member(self):
        """
        Try to add memberships and renew them.
        """
        response = self.client.get(reverse("member:club_add_member", args=(Club.objects.get(name="BDE").pk,)))
        self.assertEqual(response.status_code, 200)

        user = User.objects.create(username="totototo")
        user.profile.registration_valid = True
        user.profile.email_confirmed = True
        user.profile.save()
        user.save()

        # We create a club without any parent and one club with parent BDE (that is the club Kfet)
        for bde_parent in False, True:
            if bde_parent:
                club = Club.objects.get(name="Kfet")
            else:
                club = Club.objects.create(
                    name="Second club " + ("with BDE" if bde_parent else "without BDE"),
                    parent_club=None,
                    email="newclub@example.com",
                    require_memberships=True,
                    membership_fee_paid=1000,
                    membership_fee_unpaid=500,
                    membership_start=date.today(),
                    membership_end=date.today() + timedelta(days=366),
                    membership_duration=366,
                )

            response = self.client.get(reverse("member:club_add_member", args=(club.pk,)))
            self.assertEqual(response.status_code, 200)

            # Create a new membership
            response = self.client.post(reverse("member:club_add_member", args=(club.pk,)), data=dict(
                user=user.pk,
                date_start="{:%Y-%m-%d}".format(date.today()),
                soge=False,
                credit_type=NoteSpecial.objects.get(special_type="Espèces").id,
                credit_amount=4200,
                last_name="TOTO",
                first_name="Toto",
                bank="Le matelas",
            ))
            self.assertRedirects(response, user.profile.get_absolute_url(), 302, 200)

            self.assertTrue(Membership.objects.filter(user=user, club=club).exists())

            # Membership is sent to the past to check renewals
            membership = Membership.objects.get(user=user, club=club)
            self.assertTrue(membership.valid)
            membership.date_start = date(year=2000, month=1, day=1)
            membership.date_end = date(year=2000, month=12, day=31)
            membership.save()
            self.assertFalse(membership.valid)

            response = self.client.get(reverse("member:club_members", args=(club.pk,)) + "?only_active=0")
            self.assertEqual(response.status_code, 200)

            bde_membership = self.bde_membership
            if bde_parent:
                bde_membership = Membership.objects.get(club__name="BDE", user=user)
                bde_membership.date_start = date(year=2000, month=1, day=1)
                bde_membership.date_end = date(year=2000, month=12, day=31)
                bde_membership.save()

            response = self.client.get(reverse("member:club_renew_membership", args=(bde_membership.pk,)))
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse("member:club_renew_membership", args=(membership.pk,)))
            self.assertEqual(response.status_code, 200)

            # Renew membership
            response = self.client.post(reverse("member:club_renew_membership", args=(membership.pk,)), data=dict(
                user=user.pk,
                date_start="{:%Y-%m-%d}".format(date.today()),
                soge=bde_parent,
                credit_type=NoteSpecial.objects.get(special_type="Chèque").id,
                credit_amount=14242,
                last_name="TOTO",
                first_name="Toto",
                bank="Bank",
            ))
            self.assertRedirects(response, user.profile.get_absolute_url(), 302, 200)

            response = self.client.get(club.get_absolute_url())
            self.assertEqual(response.status_code, 200)

    def test_auto_join_kfet_when_join_bde_with_soge(self):
        """
        When we join the BDE club with a Soge registration, a Kfet membership is automatically created.
        We check that it is the case.
        """
        user = User.objects.create(username="new1A")
        user.profile.registration_valid = True
        user.profile.email_confirmed = True
        user.profile.save()
        user.save()

        bde = Club.objects.get(name="BDE")
        kfet = Club.objects.get(name="Kfet")

        response = self.client.post(reverse("member:club_add_member", args=(bde.pk,)), data=dict(
            user=user.pk,
            date_start="{:%Y-%m-%d}".format(date.today()),
            soge=True,
            credit_type=NoteSpecial.objects.get(special_type="Virement bancaire").id,
            credit_amount=(bde.membership_fee_paid + kfet.membership_fee_paid) / 100,
            last_name="TOTO",
            first_name="Toto",
            bank="Société générale",
        ))
        self.assertRedirects(response, user.profile.get_absolute_url(), 302, 200)

        self.assertTrue(Membership.objects.filter(user=user, club=bde).exists())
        self.assertTrue(Membership.objects.filter(user=user, club=kfet).exists())
        self.assertTrue(SogeCredit.objects.filter(user=user).exists())

    def test_change_roles(self):
        """
        Check to change the roles of a membership.
        """
        response = self.client.get(reverse("member:club_manage_roles", args=(self.membership.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("member:club_manage_roles", args=(self.membership.pk,)), data=dict(
            roles=[role.id for role in Role.objects.filter(
                Q(name="Membre de club") | Q(name="Trésorier·ère de club") | Q(name="Bureau de club")).all()],
        ))
        self.assertRedirects(response, self.user.profile.get_absolute_url(), 302, 200)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.roles.count(), 3)

    def test_render_user_list(self):
        """
        Display the user search page.
        """
        response = self.client.get(reverse("member:user_list"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("member:user_list") + "?search=toto")
        self.assertEqual(response.status_code, 200)

    def test_render_user_detail(self):
        """
        Display the user detail page.
        """
        response = self.client.get(self.user.profile.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_render_user_update(self):
        """
        Update some data about the user.
        """
        response = self.client.get(reverse("member:user_update_profile", args=(self.user.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("member:user_update_profile", args=(self.user.pk,)), data=dict(
            first_name="Toto",
            last_name="Toto",
            username="toto changed",
            email="updated@example.com",
            phone_number="+33600000000",
            section="",
            department="A0",
            promotion=timezone.now().year,
            address="Earth",
            paid=True,
            ml_events_registration="en",
            ml_sports_registration=True,
            ml_art_registration=True,
            report_frequency=7,
        ))
        self.assertRedirects(response, self.user.profile.get_absolute_url(), 302, 200)
        self.assertTrue(User.objects.filter(username="toto changed").exists())
        self.assertTrue(Profile.objects.filter(address="Earth").exists())
        self.assertTrue(Alias.objects.filter(normalized_name="totochanged").exists())

    def test_render_user_update_picture(self):
        """
        Update the note picture of the user.
        """
        response = self.client.get(reverse("member:user_update_pic", args=(self.user.pk,)))
        self.assertEqual(response.status_code, 200)

        old_pic = self.user.note.display_image

        with open("apps/member/static/member/img/default_picture.png", "rb") as f:
            image = SimpleUploadedFile("image.png", f.read(), "image/png")
            response = self.client.post(reverse("member:user_update_pic", args=(self.user.pk,)), dict(
                image=image,
                x=0,
                y=0,
                width=200,
                height=200,
            ))
            self.assertRedirects(response, self.user.profile.get_absolute_url(), 302, 200)

        self.user.note.refresh_from_db()
        self.assertTrue(os.path.exists(self.user.note.display_image.path))
        os.remove(self.user.note.display_image.path)

        self.user.note.display_image = old_pic
        self.user.note.save()

    def test_render_user_aliases(self):
        """
        Display the list of aliases of the user.
        """
        # Alias creation and deletion is already tested in the note app
        response = self.client.get(reverse("member:user_alias", args=(self.user.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_manage_auth_token(self):
        """
        Display the page to see the API authentication token, see it and regenerate it.
        :return:
        """
        response = self.client.get(reverse("member:auth_token"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("member:auth_token") + "?view")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("member:auth_token") + "?regenerate")
        self.assertRedirects(response, reverse("member:auth_token") + "?view", 302, 200)

    def test_random_coverage(self):
        # Useless, only for coverage
        self.assertEqual(str(self.user), str(self.user.profile))
        self.user.profile.promotion = None
        self.assertEqual(self.user.profile.ens_year, 0)
        self.membership.date_end = None
        self.assertTrue(self.membership.valid)

    def test_nk15_hasher(self):
        """
        Test that NK15 passwords are successfully imported.
        """
        salt = "42"
        password = "strongpassword42"
        hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        self.user.password = "custom_nk15$1$" + salt + "|" + hashed
        self.user.save()
        self.assertTrue(self.user.check_password(password))


class TestMemberAPI(TestAPI):
    def setUp(self) -> None:
        super().setUp()

        self.user.profile.registration_valid = True
        self.user.profile.email_confirmed = True
        self.user.profile.phone_number = "0600000000"
        self.user.profile.section = "1A0"
        self.user.profile.department = "A0"
        self.user.profile.address = "Earth"
        self.user.profile.save()

        self.club = Club.objects.create(
            name="totoclub",
            parent_club=Club.objects.get(name="BDE"),
            membership_start=date(year=1970, month=1, day=1),
            membership_end=date(year=2040, month=1, day=1),
            membership_duration=365 * 10,
        )
        self.bde_membership = Membership.objects.create(user=self.user, club=Club.objects.get(name="BDE"))
        self.membership = Membership.objects.create(user=self.user, club=self.club)
        self.membership.roles.add(Role.objects.get(name="Bureau de club"))
        self.membership.save()

    def test_member_api(self):
        """
        Load API pages for the member app and test all filters
        """
        self.check_viewset(ClubViewSet, "/api/members/club/")
        self.check_viewset(ProfileViewSet, "/api/members/profile/")
        self.check_viewset(MembershipViewSet, "/api/members/membership/")
