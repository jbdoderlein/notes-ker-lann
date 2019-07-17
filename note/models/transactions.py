# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .notes import Note

"""
Defines transactions
"""


class TransactionTemplate(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )
    destination = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
        related_name='+',  # no reverse
        verbose_name=_('destination'),
    )
    amount = models.PositiveIntegerField(
        verbose_name=_('amount'),
        help_text=_('in centimes'),
    )
    template_type = models.CharField(
        verbose_name=_('type'),
        max_length=31
    )

    class Meta:
        verbose_name = _("transaction template")
        verbose_name_plural = _("transaction templates")


class Transaction(models.Model):
    source = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('source'),
    )
    destination = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('destination'),
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name=_('quantity'),
    )
    amount = models.PositiveIntegerField(
        verbose_name=_('amount'),
    )
    transaction_type = models.CharField(
        verbose_name=_('type'),
        max_length=31,
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    valid = models.NullBooleanField(
        verbose_name=_('valid'),
    )

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")


class MembershipTransaction(Transaction):
    membership = models.OneToOneField(
        'member.Membership',
        on_delete=models.PROTECT,
        related_name='transaction',
    )

    class Meta:
        verbose_name = _("membership transaction")
        verbose_name_plural = _("membership transactions")
