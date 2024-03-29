# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from api.tests import TestAPI
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from member.models import Membership, Club
from note.models import SpecialTransaction, NoteSpecial, Transaction

from ..api.views import InvoiceViewSet, ProductViewSet, RemittanceViewSet, RemittanceTypeViewSet
from ..models import Invoice, Product, Remittance, RemittanceType


class TestInvoices(TestCase):
    """
    Check that invoices can be created and rendered properly.
    """
    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            username="admintoto",
            password="totototo",
            email="admin@example.com",
        )
        self.client.force_login(self.user)
        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

        self.invoice = Invoice.objects.create(
            id=1,
            object="Object",
            description="Description",
            name="Me",
            address="Earth",
            acquitted=False,
        )
        self.product = Product.objects.create(
            invoice=self.invoice,
            designation="Product",
            quantity=3,
            amount=3.14,
        )

    def test_admin_page(self):
        """
        Display the invoice admin page.
        """
        response = self.client.get(reverse("admin:index") + "treasury/invoice/")
        self.assertEqual(response.status_code, 200)

    def test_invoices_list(self):
        """
        Display the list of invoices.
        """
        response = self.client.get(reverse("treasury:invoice_list"))
        self.assertEqual(response.status_code, 200)

    def test_invoice_create(self):
        """
        Try to create a new invoice.
        """
        response = self.client.get(reverse("treasury:invoice_create"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("treasury:invoice_create"), data={
            "id": 42,
            "object": "Same object",
            "description": "Longer description",
            "name": "Me and others",
            "address": "Alwways earth",
            "acquitted": True,
            "products-0-designation": "Designation",
            "products-0-quantity": 1,
            "products-0-amount": 42,
            "products-TOTAL_FORMS": 1,
            "products-INITIAL_FORMS": 0,
            "products-MIN_NUM_FORMS": 0,
            "products-MAX_NUM_FORMS": 1000,
        })
        self.assertRedirects(response, reverse("treasury:invoice_list"), 302, 200)
        self.assertTrue(Invoice.objects.filter(object="Same object", id=42).exists())
        self.assertTrue(Product.objects.filter(designation="Designation", invoice_id=42).exists())
        self.assertTrue(Invoice.objects.get(id=42).tex)

    def test_invoice_update(self):
        """
        Try to update an invoice.
        """
        response = self.client.get(reverse("treasury:invoice_update", args=(self.invoice.id,)))
        self.assertEqual(response.status_code, 200)

        data = {
            "object": "Same object",
            "description": "Longer description",
            "name": "Me and others",
            "address": "Always earth",
            "acquitted": True,
            "locked": True,
            "products-0-designation": "Designation",
            "products-0-quantity": 1,
            "products-0-amount": 4200,
            "products-1-designation": "Second designation",
            "products-1-quantity": 5,
            "products-1-amount": -1800,
            "products-TOTAL_FORMS": 2,
            "products-INITIAL_FORMS": 0,
            "products-MIN_NUM_FORMS": 0,
            "products-MAX_NUM_FORMS": 1000,
        }

        response = self.client.post(reverse("treasury:invoice_update", args=(self.invoice.id,)), data=data)
        self.assertRedirects(response, reverse("treasury:invoice_list"), 302, 200)
        self.invoice.refresh_from_db()
        self.assertTrue(Invoice.objects.filter(pk=1, object="Same object", locked=True).exists())
        self.assertTrue(Product.objects.filter(designation="Second designation", invoice_id=1).exists())

        # Resend the same data, but the invoice is locked.
        response = self.client.get(reverse("treasury:invoice_update", args=(self.invoice.id,)))
        self.assertTrue(response.status_code, 200)
        response = self.client.post(reverse("treasury:invoice_update", args=(self.invoice.id,)), data=data)
        self.assertTrue(response.status_code, 200)

    def test_delete_invoice(self):
        """
        Try to delete an invoice.
        """
        response = self.client.get(reverse("treasury:invoice_delete", args=(self.invoice.id,)))
        self.assertEqual(response.status_code, 200)

        # Can't delete a locked invoice
        self.invoice.locked = True
        self.invoice.save()
        response = self.client.delete(reverse("treasury:invoice_delete", args=(self.invoice.id,)))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Invoice.objects.filter(pk=self.invoice.id).exists())

        # Unlock invoice and truly delete it.
        self.invoice.locked = False
        self.invoice._force_save = True
        self.invoice.save()
        response = self.client.delete(reverse("treasury:invoice_delete", args=(self.invoice.id,)))
        self.assertRedirects(response, reverse("treasury:invoice_list"), 302, 200)
        self.assertFalse(Invoice.objects.filter(pk=self.invoice.id).exists())

    def test_invoice_render_pdf(self):
        """
        Generate the PDF file of an invoice.
        """
        response = self.client.get(reverse("treasury:invoice_render", args=(self.invoice.id,)))
        self.assertEqual(response.status_code, 200)

    def test_invoice_api(self):
        """
        Load some API pages
        """
        response = self.client.get("/api/treasury/invoice/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/treasury/product/")
        self.assertEqual(response.status_code, 200)


class TestRemittances(TestCase):
    """
    Create some credits and close remittances.
    """

    fixtures = ('initial',)

    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            username="admintoto",
            password="totototo",
            email="admin@example.com",
        )
        self.client.force_login(self.user)
        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

        self.credit = SpecialTransaction.objects.create(
            source=NoteSpecial.objects.get(special_type="Chèque"),
            destination=self.user.note,
            amount=4200,
            reason="Credit",
            last_name="TOTO",
            first_name="Toto",
        )

        self.second_credit = SpecialTransaction.objects.create(
            source=self.user.note,
            destination=NoteSpecial.objects.get(special_type="Chèque"),
            amount=424200,
            reason="Second credit",
            last_name="TOTO",
            first_name="Toto",
        )

        self.remittance = Remittance.objects.create(
            remittance_type=RemittanceType.objects.get(),
            comment="Test remittance",
            closed=False,
        )
        self.credit.specialtransactionproxy.remittance = self.remittance
        self.credit.specialtransactionproxy.save()

    def test_admin_page(self):
        """
        Load the admin page.
        """
        response = self.client.get(reverse("admin:index") + "treasury/remittance/")
        self.assertEqual(response.status_code, 200)

    def test_remittances_list(self):
        """
        Display the remittance list.
        :return:
        """
        response = self.client.get(reverse("treasury:remittance_list"))
        self.assertEqual(response.status_code, 200)

    def test_remittance_create(self):
        """
        Create a new Remittance.
        """
        response = self.client.get(reverse("treasury:remittance_create"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("treasury:remittance_create"), data=dict(
            remittance_type=RemittanceType.objects.get().pk,
            comment="Created remittance",
        ))
        self.assertRedirects(response, reverse("treasury:remittance_list"), 302, 200)
        self.assertTrue(Remittance.objects.filter(comment="Created remittance").exists())

    def test_remittance_update(self):
        """
        Update an existing remittance.
        """
        response = self.client.get(reverse("treasury:remittance_update", args=(self.remittance.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("treasury:remittance_update", args=(self.remittance.pk,)), data=dict(
            comment="Updated remittance",
        ))
        self.assertRedirects(response, reverse("treasury:remittance_list"), 302, 200)
        self.assertTrue(Remittance.objects.filter(comment="Updated remittance").exists())

    def test_remittance_close(self):
        """
        Try to close an open remittance.
        """
        response = self.client.get(reverse("treasury:remittance_update", args=(self.remittance.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("treasury:remittance_update", args=(self.remittance.pk,)), data=dict(
            comment="Closed remittance",
            close=True,
        ))
        self.assertRedirects(response, reverse("treasury:remittance_list"), 302, 200)
        self.assertTrue(Remittance.objects.filter(comment="Closed remittance", closed=True).exists())

    def test_remittance_link_transaction(self):
        """
        Link a transaction to an open remittance.
        """
        response = self.client.get(reverse("treasury:link_transaction", args=(self.credit.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("treasury:link_transaction", args=(self.credit.pk,)), data=dict(
            remittance=self.remittance.pk,
            last_name="Last Name",
            first_name="First Name",
        ))
        self.assertRedirects(response, reverse("treasury:remittance_list"), 302, 200)
        self.credit.refresh_from_db()
        self.assertEqual(self.credit.last_name, "Last Name")
        self.assertEqual(self.remittance.transactions.count(), 1)

        response = self.client.get(reverse("treasury:unlink_transaction", args=(self.credit.pk,)))
        self.assertRedirects(response, reverse("treasury:remittance_list"), 302, 200)

    def test_invoice_api(self):
        """
        Load some API pages
        """
        response = self.client.get("/api/treasury/remittance_type/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/treasury/remittance/")
        self.assertEqual(response.status_code, 200)


class TestTreasuryAPI(TestAPI):
    def setUp(self) -> None:
        super().setUp()

        self.invoice = Invoice.objects.create(
            id=1,
            object="Object",
            description="Description",
            name="Me",
            address="Earth",
            acquitted=False,
        )
        self.product = Product.objects.create(
            invoice=self.invoice,
            designation="Product",
            quantity=3,
            amount=3.14,
        )

        self.credit = SpecialTransaction.objects.create(
            source=NoteSpecial.objects.get(special_type="Chèque"),
            destination=self.user.note,
            amount=4200,
            reason="Credit",
            last_name="TOTO",
            first_name="Toto"
        )

        self.remittance = Remittance.objects.create(
            remittance_type=RemittanceType.objects.get(),
            comment="Test remittance",
            closed=False,
        )
        self.credit.specialtransactionproxy.remittance = self.remittance
        self.credit.specialtransactionproxy.save()

        self.kfet = Club.objects.get(name="BDA")
        self.bde = self.kfet.parent_club

        self.kfet_membership = Membership(
            user=self.user,
            club=self.kfet,
        )
        self.kfet_membership._force_renew_parent = True
        self.kfet_membership.save()

    def test_invoice_api(self):
        """
        Load Invoice API page and test all filters and permissions
        """
        self.check_viewset(InvoiceViewSet, "/api/treasury/invoice/")

    def test_product_api(self):
        """
        Load Product API page and test all filters and permissions
        """
        self.check_viewset(ProductViewSet, "/api/treasury/product/")

    def test_remittance_api(self):
        """
        Load Remittance API page and test all filters and permissions
        """
        self.check_viewset(RemittanceViewSet, "/api/treasury/remittance/")

    def test_remittance_type_api(self):
        """
        Load RemittanceType API page and test all filters and permissions
        """
        self.check_viewset(RemittanceTypeViewSet, "/api/treasury/remittance_type/")

