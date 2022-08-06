# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
import datetime
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from member.models import Club, Membership
from note.models import NoteSpecial, SpecialTransaction, MembershipTransaction, NoteUser


class Invoice(models.Model):
    """
    An invoice model that can generates a true invoice.
    """

    id = models.PositiveIntegerField(
        primary_key=True,
        verbose_name=_("Invoice identifier"),
    )

    bde = models.CharField(
        max_length=32,
        default='BDE',
        choices=(
            ('BDE', 'BDE'),
        ),
        verbose_name=_("BDE"),
    )

    object = models.CharField(
        max_length=255,
        verbose_name=_("Object"),
    )

    description = models.TextField(
        verbose_name=_("Description")
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )

    address = models.TextField(
        verbose_name=_("Address"),
    )

    date = models.DateField(
        default=date.today,
        verbose_name=_("Date"),
    )

    acquitted = models.BooleanField(
        verbose_name=_("Acquitted"),
        default=False,
    )

    locked = models.BooleanField(
        verbose_name=_("Locked"),
        help_text=_("An invoice can't be edited when it is locked."),
        default=False,
    )

    tex = models.TextField(
        default="",
        verbose_name=_("tex source"),
    )

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        When an invoice is generated, we store the tex source.
        The advantage is to never change the template.
        Warning: editing this model regenerate the tex source, so be careful.
        """

        old_invoice = Invoice.objects.filter(id=self.id)
        if old_invoice.exists():
            if old_invoice.get().locked and not self._force_save:
                raise ValidationError(_("This invoice is locked and can no longer be edited."))

        products = self.products.all()

        self.place = "Gif-sur-Yvette"
        self.my_name = "BDE ENS Cachan"
        self.my_address_street = "4 avenue des Sciences"
        self.my_city = "91190 Gif-sur-Yvette"
        self.bank_code = 30003
        self.desk_code = 3894
        self.account_number = 37280662
        self.rib_key = 14
        self.bic = "SOGEFRPP"

        # Fill the template with the information
        self.tex = render_to_string("treasury/invoice_sample.tex", dict(obj=self, products=products))

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")

    def __str__(self):
        return _("Invoice #{id}").format(id=self.id)


class Product(models.Model):
    """
    Product that appears on an invoice.
    """

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("invoice"),
    )

    designation = models.CharField(
        max_length=255,
        verbose_name=_("Designation"),
    )

    quantity = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        verbose_name=_("Quantity"),
        validators=[MinValueValidator(0)],
    )

    amount = models.IntegerField(
        verbose_name=_("Unit price"),
    )

    @property
    def amount_euros(self):
        return "{:.2f}".format(self.amount / 100)

    @property
    def total(self):
        return self.quantity * self.amount

    @property
    def total_euros(self):
        return "{:.2f}".format(self.total / 100)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return f"{self.designation} ({self.invoice})"


class RemittanceType(models.Model):
    """
    Store what kind of remittances can be stored.
    """

    note = models.OneToOneField(
        NoteSpecial,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.note)

    class Meta:
        verbose_name = _("remittance type")
        verbose_name_plural = _("remittance types")


class Remittance(models.Model):
    """
    Treasurers want to regroup checks or bank transfers in bank remittances.
    """

    date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Date"),
    )

    remittance_type = models.ForeignKey(
        RemittanceType,
        on_delete=models.PROTECT,
        verbose_name=_("Type"),
    )

    comment = models.CharField(
        max_length=255,
        verbose_name=_("Comment"),
    )

    closed = models.BooleanField(
        default=False,
        verbose_name=_("Closed"),
    )

    class Meta:
        verbose_name = _("remittance")
        verbose_name_plural = _("remittances")

    @property
    def transactions(self):
        """
        :return: Transactions linked to this remittance.
        """
        if not self.pk:
            return SpecialTransaction.objects.none()
        return SpecialTransaction.objects.filter(specialtransactionproxy__remittance=self)

    def count(self):
        """
        Linked transactions count.
        """
        return self.transactions.count()

    @property
    def amount(self):
        """
        Total amount of the remittance.
        """
        return sum(transaction.total for transaction in self.transactions.all())

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Check if all transactions have the right type.
        if self.transactions.exists() and self.transactions.filter(~Q(source=self.remittance_type.note)).exists():
            raise ValidationError("All transactions in a remittance must have the same type")

        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return _("Remittance #{:d}: {}").format(self.id, self.comment, )


class SpecialTransactionProxy(models.Model):
    """
    In order to keep modularity, we don't that the Note app depends on the treasury app.
    That's why we create a proxy in this app, to link special transactions and remittances.
    If it isn't very clean, it does what we want.
    """

    transaction = models.OneToOneField(
        SpecialTransaction,
        on_delete=models.CASCADE,
    )

    remittance = models.ForeignKey(
        Remittance,
        on_delete=models.PROTECT,
        null=True,
        related_name="transaction_proxies",
        verbose_name=_("Remittance"),
    )

    class Meta:
        verbose_name = _("special transaction proxy")
        verbose_name_plural = _("special transaction proxies")

    def __str__(self):
        return str(self.transaction)
