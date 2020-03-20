# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _


class Billing(models.Model):
    id = models.PositiveIntegerField(
        primary_key=True,
        verbose_name=_("Billing identifier"),
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

    subject = models.CharField(
        max_length=255,
        verbose_name=_("Subject"),
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

    place = models.CharField(
        max_length=255,
        default="Cachan",
        verbose_name=_("Place"),
    )

    my_name = models.CharField(
        max_length=255,
        default="BDE ENS Cachan",
        verbose_name=_("My name"),
    )

    my_address_street = models.CharField(
        max_length=255,
        default="61 avenue du Président Wilson",
        verbose_name=_("My street address"),
    )

    my_city = models.CharField(
        max_length=255,
        default="94230 Cachan",
        verbose_name=_("My city"),
    )

    bank_code = models.IntegerField(
        default=30003,
        verbose_name=_("Bank code"),
    )

    desk_code = models.IntegerField(
        default=3894,
        verbose_name=_("Desk code"),
    )

    account_number = models.IntegerField(
        default=37280662,
        verbose_name=_("Account number"),
    )

    rib_key = models.SmallIntegerField(
        default=14,
        verbose_name=_("RIB Key")
    )

    bic = models.CharField(
        max_length=16,
        default="SOGEFRPP",
        verbose_name=_("BIC Code")
    )


class Product(models.Model):
    billing = models.ForeignKey(
        Billing,
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
    def total(self):
        return self.quantity * self.amount
