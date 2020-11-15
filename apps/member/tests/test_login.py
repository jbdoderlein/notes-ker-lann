# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

"""
Test that login page still works
"""


class TemplateLoggedOutTests(TestCase):
    def test_login_page(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)


class TemplateLoggedInTests(TestCase):
    fixtures = ('initial', )

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            password="adminadmin",
            email="admin@example.com",
        )
        self.client.force_login(self.user)
        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

    def test_login_page(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        self.client.logout()

        response = self.client.post('/accounts/login/', data=dict(
            username="admin",
            password="adminadmin",
            permission_mask=3,
        ))
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, 302, 302)

    def test_logout(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)

    def test_admin_index(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_accounts_password_reset(self):
        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)
