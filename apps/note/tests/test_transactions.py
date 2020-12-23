# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from api.tests import TestAPI
from member.models import Club, Membership
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from permission.models import Role

from ..api.views import AliasViewSet, ConsumerViewSet, NotePolymorphicViewSet, TemplateCategoryViewSet,\
    TransactionTemplateViewSet, TransactionViewSet
from ..models import NoteUser, Transaction, TemplateCategory, TransactionTemplate, RecurrentTransaction, \
    MembershipTransaction, SpecialTransaction, NoteSpecial, Alias, Note


class TestTransactions(TestCase):
    fixtures = ('initial', )

    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            username="toto",
            password="totototo",
            email="toto@example.com",
        )

        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()
        self.client.force_login(self.user)

        membership = Membership.objects.create(club=Club.objects.get(name="BDE"), user=self.user)
        membership.roles.add(Role.objects.get(name="Respo info"))
        membership.save()
        Membership.objects.create(club=Club.objects.get(name="Kfet"), user=self.user)
        self.user.note.refresh_from_db()

        self.second_user = User.objects.create(
            username="toto2",
        )
        # Non superusers have no note until the registration get validated
        NoteUser.objects.create(user=self.second_user)

        self.club = Club.objects.create(
            name="clubtoto",
        )

        self.transaction = Transaction.objects.create(
            source=self.second_user.note,
            destination=self.user.note,
            amount=4200,
            reason="Test transaction",
        )
        self.user.note.refresh_from_db()
        self.second_user.note.refresh_from_db()

        self.category = TemplateCategory.objects.create(name="Test")
        self.template = TransactionTemplate.objects.create(
            name="Test",
            destination=self.club.note,
            category=self.category,
            amount=100,
            description="Test template",
        )

    def test_admin_pages(self):
        """
        Load some admin pages to check that they render successfully.
        """
        response = self.client.get(reverse("admin:index") + "note/note/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/transaction/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/transaction/" + str(self.transaction.pk) + "/change/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/transaction/add/?ct_id="
                                   + str(ContentType.objects.get_for_model(Transaction).id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/transaction/add/?ct_id="
                                   + str(ContentType.objects.get_for_model(RecurrentTransaction).id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/transaction/add/?ct_id="
                                   + str(ContentType.objects.get_for_model(MembershipTransaction).id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/transaction/add/?ct_id="
                                   + str(ContentType.objects.get_for_model(SpecialTransaction).id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/transactiontemplate/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:index") + "note/templatecategory/")
        self.assertEqual(response.status_code, 200)

    def test_render_transfer_page(self):
        response = self.client.get(reverse("note:transfer"))
        self.assertEqual(response.status_code, 200)

    def test_transfer_api(self):
        old_user_balance = self.user.note.balance
        old_second_user_balance = self.second_user.note.balance
        quantity = 3
        amount = 314
        total = quantity * amount
        response = self.client.post("/api/note/transaction/transaction/", data=dict(
            quantity=quantity,
            amount=amount,
            reason="Transaction through API",
            valid=True,
            polymorphic_ctype=ContentType.objects.get_for_model(Transaction).id,
            resourcetype="Transaction",
            source=self.user.note.id,
            source_alias=self.user.username,
            destination=self.second_user.note.id,
            destination_alias=self.second_user.username,
        ))
        self.assertEqual(response.status_code, 201)  # 201 = Created
        self.assertTrue(Transaction.objects.filter(reason="Transaction through API").exists())

        self.user.note.refresh_from_db()
        self.second_user.note.refresh_from_db()

        self.assertTrue(self.user.note.balance == old_user_balance - total)
        self.assertTrue(self.second_user.note.balance == old_second_user_balance + total)

        self.test_render_transfer_page()

    def test_credit_api(self):
        old_user_balance = self.user.note.balance
        amount = 4242
        special_type = NoteSpecial.objects.first()
        response = self.client.post("/api/note/transaction/transaction/", data=dict(
            quantity=1,
            amount=amount,
            reason="Credit through API",
            valid=True,
            polymorphic_ctype=ContentType.objects.get_for_model(SpecialTransaction).id,
            resourcetype="SpecialTransaction",
            source=special_type.id,
            source_alias=str(special_type),
            destination=self.user.note.id,
            destination_alias=self.user.username,
            last_name="TOTO",
            first_name="Toto",
        ))

        self.assertEqual(response.status_code, 201)  # 201 = Created
        self.assertTrue(Transaction.objects.filter(reason="Credit through API").exists())
        self.user.note.refresh_from_db()
        self.assertTrue(self.user.note.balance == old_user_balance + amount)

        self.test_render_transfer_page()

    def test_debit_api(self):
        old_user_balance = self.user.note.balance
        amount = 4242
        special_type = NoteSpecial.objects.first()
        response = self.client.post("/api/note/transaction/transaction/", data=dict(
            quantity=1,
            amount=amount,
            reason="Debit through API",
            valid=True,
            polymorphic_ctype=ContentType.objects.get_for_model(SpecialTransaction).id,
            resourcetype="SpecialTransaction",
            source=self.user.note.id,
            source_alias=self.user.username,
            destination=special_type.id,
            destination_alias=str(special_type),
            last_name="TOTO",
            first_name="Toto",
        ))
        self.assertEqual(response.status_code, 201)  # 201 = Created
        self.assertTrue(Transaction.objects.filter(reason="Debit through API").exists())
        self.user.note.refresh_from_db()
        self.assertTrue(self.user.note.balance == old_user_balance - amount)

        self.test_render_transfer_page()

    def test_render_consos_page(self):
        response = self.client.get(reverse("note:consos"))
        self.assertEqual(response.status_code, 200)

    def test_consumption_api(self):
        old_user_balance = self.user.note.balance
        old_club_balance = self.club.note.balance
        quantity = 2
        template = self.template
        total = quantity * template.amount
        response = self.client.post("/api/note/transaction/transaction/", data=dict(
            quantity=quantity,
            amount=template.amount,
            reason="Consumption through API (" + template.name + ")",
            valid=True,
            polymorphic_ctype=ContentType.objects.get_for_model(RecurrentTransaction).id,
            resourcetype="RecurrentTransaction",
            source=self.user.note.id,
            source_alias=self.user.username,
            destination=self.club.note.id,
            destination_alias=self.second_user.username,
            template=template.id,
        ))
        self.assertEqual(response.status_code, 201)  # 201 = Created
        self.assertTrue(Transaction.objects.filter(destination=self.club.note).exists())

        self.user.note.refresh_from_db()
        self.club.note.refresh_from_db()

        self.assertTrue(self.user.note.balance == old_user_balance - total)
        self.assertTrue(self.club.note.balance == old_club_balance + total)

        self.test_render_consos_page()

    def test_invalidate_transaction(self):
        old_second_user_balance = self.second_user.note.balance
        old_user_balance = self.user.note.balance
        total = self.transaction.total
        response = self.client.patch("/api/note/transaction/transaction/" + str(self.transaction.pk) + "/", data=dict(
            valid=False,
            resourcetype="Transaction",
            invalidity_reason="Test invalidate",
        ), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Transaction.objects.filter(valid=False, invalidity_reason="Test invalidate").exists())

        self.second_user.note.refresh_from_db()
        self.user.note.refresh_from_db()

        self.assertTrue(self.second_user.note.balance == old_second_user_balance + total)
        self.assertTrue(self.user.note.balance == old_user_balance - total)

        self.test_render_transfer_page()
        self.test_render_consos_page()

        # Now we check if we can revalidate
        old_second_user_balance = self.second_user.note.balance
        old_user_balance = self.user.note.balance
        total = self.transaction.total
        response = self.client.patch("/api/note/transaction/transaction/" + str(self.transaction.pk) + "/", data=dict(
            valid=True,
            resourcetype="Transaction",
        ), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Transaction.objects.filter(valid=True, pk=self.transaction.pk).exists())

        self.second_user.note.refresh_from_db()
        self.user.note.refresh_from_db()

        self.assertTrue(self.second_user.note.balance == old_second_user_balance - total)
        self.assertTrue(self.user.note.balance == old_user_balance + total)

        self.test_render_transfer_page()
        self.test_render_consos_page()

    def test_render_template_list(self):
        response = self.client.get(reverse("note:template_list") + "?search=test")
        self.assertEqual(response.status_code, 200)

    def test_render_template_create(self):
        response = self.client.get(reverse("note:template_create"))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("note:template_create"), data=dict(
            name="Test create button",
            destination=self.club.note.pk,
            category=self.category.pk,
            amount=4200,
            description="We have created a button",
            highlighted=True,
            display=True,
        ))
        self.assertRedirects(response, reverse("note:template_list"), 302, 200)
        self.assertTrue(TransactionTemplate.objects.filter(name="Test create button").exists())

    def test_render_template_update(self):
        response = self.client.get(self.template.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.template.get_absolute_url(), data=dict(
            name="Test update button",
            destination=self.club.note.pk,
            category=self.category.pk,
            amount=4200,
            description="We have updated a button",
            highlighted=True,
            display=True,
        ))
        self.assertRedirects(response, reverse("note:template_list"), 302, 200)
        self.assertTrue(TransactionTemplate.objects.filter(name="Test update button", pk=self.template.pk).exists())

        # Check that the price history renders properly
        response = self.client.post(self.template.get_absolute_url(), data=dict(
            name="Test price history",
            destination=self.club.note.pk,
            category=self.category.pk,
            amount=4200,
            description="We have updated a button",
            highlighted=True,
            display=True,
        ))
        self.assertRedirects(response, reverse("note:template_list"), 302, 200)
        self.assertTrue(TransactionTemplate.objects.filter(name="Test price history", pk=self.template.pk).exists())
        response = self.client.get(reverse("note:template_update", args=(self.template.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_render_search_transactions(self):
        response = self.client.get(reverse("note:transactions", args=(self.user.note.pk,)), data=dict(
            source=self.second_user.note.alias.first().id,
            destination=self.user.note.alias.first().id,
            type=[ContentType.objects.get_for_model(Transaction).id],
            reason="test",
            valid=True,
            amount_gte=0,
            amount_lte=42424242,
            created_after="2000-01-01 00:00",
            created_before="2042-12-31 21:42",
        ))
        self.assertEqual(response.status_code, 200)

    def test_delete_transaction(self):
        # Transactions can't be deleted with a normal usage, but it is possible through the admin interface.
        old_second_user_balance = self.second_user.note.balance
        old_user_balance = self.user.note.balance
        total = self.transaction.total

        self.transaction.delete()
        self.second_user.note.refresh_from_db()
        self.user.note.refresh_from_db()

        self.assertTrue(self.second_user.note.balance == old_second_user_balance + total)
        self.assertTrue(self.user.note.balance == old_user_balance - total)

    def test_calculate_last_negative_duration(self):
        self.assertIsNone(self.user.note.last_negative_duration)
        self.assertIsNotNone(self.second_user.note.last_negative_duration)
        self.assertIsNone(self.club.note.last_negative_duration)

        Transaction.objects.create(
            source=self.club.note,
            destination=self.user.note,
            amount=2 * self.club.note.balance + 100,
            reason="Club balance is negative",
        )

        self.club.note.refresh_from_db()
        self.assertIsNotNone(self.club.note.last_negative_duration)

    def test_api_search(self):
        response = self.client.get("/api/note/note/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/note/alias/?alias=.*")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/note/consumer/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/note/transaction/transaction/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/note/transaction/template/")
        self.assertEqual(response.status_code, 200)

    def test_api_alias(self):
        response = self.client.post("/api/note/alias/", data=dict(
            name="testalias",
            note=self.user.note.id,
        ))
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Alias.objects.filter(name="testalias").exists())
        alias = Alias.objects.get(name="testalias")
        response = self.client.patch("/api/note/alias/" + str(alias.pk) + "/", dict(name="test_updated_alias"),
                                     content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Alias.objects.filter(name="test_updated_alias").exists())
        response = self.client.delete("/api/note/alias/" + str(alias.pk) + "/")
        self.assertEqual(response.status_code, 204)


class TestNoteAPI(TestAPI):
    def setUp(self) -> None:
        super().setUp()

        membership = Membership.objects.create(club=Club.objects.get(name="BDE"), user=self.user)
        membership.roles.add(Role.objects.get(name="Respo info"))
        membership.save()
        Membership.objects.create(club=Club.objects.get(name="Kfet"), user=self.user)
        self.user.note.last_negative = timezone.now()
        self.user.note.save()

        self.transaction = Transaction.objects.create(
            source=Note.objects.first(),
            destination=self.user.note,
            amount=4200,
            reason="Test transaction",
        )
        self.user.note.refresh_from_db()
        Alias.objects.create(note=self.user.note, name="I am a ¢omplex alias")

        self.category = TemplateCategory.objects.create(name="Test")
        self.template = TransactionTemplate.objects.create(
            name="Test",
            destination=Club.objects.get(name="BDE").note,
            category=self.category,
            amount=100,
            description="Test template",
        )

    def test_note_api(self):
        """
        Load API pages for the note app and test all filters
        """
        self.check_viewset(AliasViewSet, "/api/note/alias/")
        self.check_viewset(ConsumerViewSet, "/api/note/consumer/")
        self.check_viewset(NotePolymorphicViewSet, "/api/note/note/")
        self.check_viewset(TemplateCategoryViewSet, "/api/note/transaction/category/")
        self.check_viewset(TransactionTemplateViewSet, "/api/note/transaction/template/")
        self.check_viewset(TransactionViewSet, "/api/note/transaction/transaction/")
