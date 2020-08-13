# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.test import TestCase
from note.models import TransactionTemplate, TemplateCategory

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
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_admin_index(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_accounts_password_reset(self):
        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)

    def test_logout_page(self):
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 200)

    def test_transfer_page(self):
        response = self.client.get('/note/transfer/')
        self.assertEqual(response.status_code, 200)

    def test_consos_page(self):
        # Create one button and ensure that it is visible
        cat = TemplateCategory.objects.create()
        TransactionTemplate.objects.create(
            destination_id=5,
            category=cat,
            amount=0,
        )
        response = self.client.get('/note/consos/')
        self.assertEqual(response.status_code, 200)
