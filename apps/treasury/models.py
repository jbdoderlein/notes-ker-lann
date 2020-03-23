# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from note.models import NoteSpecial, SpecialTransaction


class Invoice(models.Model):
    """
    An invoice model that can generate a true invoice
    """

    id = models.PositiveIntegerField(
        primary_key=True,
        verbose_name=_("Invoice identifier"),
    )

    bde = models.CharField(
        max_length=32,
        default='Saperlistpopette.png',
        choices=(
            ('Saperlistpopette.png', 'Saper[list]popette'),
            ('Finalist.png', 'Fina[list]'),
            ('Listorique.png', '[List]orique'),
            ('Satellist.png', 'Satel[list]'),
            ('Monopolist.png', 'Monopo[list]'),
            ('Kataclist.png', 'Katac[list]'),
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
        auto_now_add=True,
        verbose_name=_("Place"),
    )

    acquitted = models.BooleanField(
        verbose_name=_("Acquitted"),
    )


class Product(models.Model):
    """
    Product that appear on an invoice.
    """

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
    )

    designation = models.CharField(
        max_length=255,
        verbose_name=_("Designation"),
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity")
    )

    amount = models.PositiveIntegerField(
        verbose_name=_("Unit price")
    )

    @property
    def amount_euros(self):
        return self.amount / 100

    @property
    def total(self):
        return self.quantity * self.amount

    @property
    def total_euros(self):
        return self.total / 100


class Remittance(models.Model):
    """
    Treasurers want to regroup checks or bank transfers in bank remittances.
    """

    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date"),
    )

    type = models.ForeignKey(
        NoteSpecial,
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

    @property
    def transactions(self):
        return SpecialTransaction.objects.filter(specialtransactionproxy__remittance=self)

    @property
    def size(self):
        return self.transactions.count()

    @property
    def amount(self):
        return sum(transaction.total for transaction in self.transactions.all())

    def full_clean(self, exclude=None, validate_unique=True):
        ret = super().full_clean(exclude, validate_unique)

        if self.transactions.filter(~Q(source=self.type)).exists():
            raise ValidationError("All transactions in a remittance must have the same type")

        return ret


class SpecialTransactionProxy(models.Model):
    """
    In order to keep modularity, we don't that the Note app depends on the treasury app.
    That's why we create a proxy in this app, to link special transactions and remittances.
    If it isn't very clean, that makes what we want.
    """

    transaction = models.OneToOneField(
        SpecialTransaction,
        on_delete=models.CASCADE,
    )

    remittance = models.ForeignKey(
        Remittance,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_("Remittance"),
    )
