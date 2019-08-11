# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .notes import Note,NoteClub

"""
Defines transactions
"""


class TransactionTemplate(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )
    destination = models.ForeignKey(
        NoteClub,
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
    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity'),
        default=1,
    )
    amount = models.PositiveIntegerField(
        verbose_name=_('amount'),
    )
    transaction_type = models.CharField(
        verbose_name=_('type'),
        max_length=31,
    )
    reason = models.CharField(
        verbose_name=_('reason'),
        max_length=255,
    )
    valid = models.BooleanField(
        verbose_name=_('valid'),
        default=True,
    )

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")

    def save(self, *args, **kwargs):
        """
        When saving, also transfer money between two notes
        """
        created = self.pk is None
        to_transfer = self.amount * self.quantity
        if not created:
            # Revert old transaction
            old_transaction = Transaction.objects.get(pk=self.pk)
            if old_transaction.valid:
                self.source.balance += to_transfer
                self.destination.balance -= to_transfer

        if self.valid:
            self.source.balance -= to_transfer
            self.destination.balance += to_transfer

        # Save notes
        self.source.save()
        self.destination.save()
        super().save(*args, **kwargs)


class MembershipTransaction(Transaction):
    membership = models.OneToOneField(
        'member.Membership',
        on_delete=models.PROTECT,
        related_name='transaction',
    )

    class Meta:
        verbose_name = _("membership transaction")
        verbose_name_plural = _("membership transactions")
