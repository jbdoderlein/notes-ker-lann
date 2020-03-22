# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _


class Invoice(models.Model):
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
