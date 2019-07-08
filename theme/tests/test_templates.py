# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.test import TestCase

"""
Test that every themed page still works
"""


class TemplateLoggedOutTests(TestCase):
    def test_login_page(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)


class TemplateLoggedInTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            password="adminadmin",
            email="admin@example.com",
        )
        self.client.force_login(self.user)

    def test_login_page(self):
        """
        Login page should redirect
        """
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 302)

    def test_admin_index(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_accounts_password_reset(self):
        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)

    def test_logout_page(self):
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 200)
