# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from member.models import Membership, Club
from note.models import NoteUser
from oauth2_provider.models import Application, AccessToken

from ..models import Role, Permission


class OAuth2TestCase(TestCase):
    fixtures = ('initial', )

    def setUp(self):
        self.user = User.objects.create(
            username="toto",
        )
        self.application = Application.objects.create(
            name="Test",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            user=self.user,
        )

    def test_oauth2_access(self):
        """
        Create a simple OAuth2 access token that only has the right to see data of the current user
        and check that this token has required access, and nothing more.
        """

        bde = Club.objects.get(name="BDE")
        view_user_perm = Permission.objects.get(pk=1)  # View own user detail

        # Create access token that has access to our own user detail
        token = AccessToken.objects.create(
            user=self.user,
            application=self.application,
            scope=f"{view_user_perm.pk}_{bde.pk}",
            token=get_random_string(64),
            expires=timezone.now() + timedelta(days=365),
        )

        # No access without token
        resp = self.client.get(f'/api/user/{self.user.pk}/')
        self.assertEqual(resp.status_code, 403)

        # Valid token but user has no membership, so the query is not returning the user object
        resp = self.client.get(f'/api/user/{self.user.pk}/', **{'Authorization': f'Bearer {token.token}'})
        self.assertEqual(resp.status_code, 404)

        # Create membership to validate permissions
        NoteUser.objects.create(user=self.user)
        membership = Membership.objects.create(user=self.user, club_id=bde.pk)
        membership.roles.add(Role.objects.get(name="Adhérent"))
        membership.save()

        # User is now a member and can now see its own user detail
        resp = self.client.get(f'/api/user/{self.user.pk}/', **{'Authorization': f'Bearer {token.token}'})
        self.assertEqual(resp.status_code, 200)

        # Token is not granted to see profile detail
        resp = self.client.get(f'/api/members/profile/{self.user.profile.pk}/',
                               **{'Authorization': f'Bearer {token.token}'})
        self.assertEqual(resp.status_code, 404)

    def test_scopes(self):
        """
        Ensure that the scopes page is loading.
        """
        self.client.force_login(self.user)

        resp = self.client.get(reverse('permission:scopes'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.application, resp.context['scopes'])
        self.assertNotIn('1_1', resp.context['scopes'][self.application])  # The user has not this permission

        # Create membership to validate permissions
        bde = Club.objects.get(name="BDE")
        NoteUser.objects.create(user=self.user)
        membership = Membership.objects.create(user=self.user, club_id=bde.pk)
        membership.roles.add(Role.objects.get(name="Adhérent"))
        membership.save()

        resp = self.client.get(reverse('permission:scopes'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.application, resp.context['scopes'])
        self.assertIn('1_1', resp.context['scopes'][self.application])  # Now the user has this permission
