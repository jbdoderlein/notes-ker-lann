# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .notes import Note, NoteClub

"""
Defines transactions
"""


class TransactionCategory(models.Model):
    """
    Defined a recurrent transaction category

    Example: food, softs, ...
    """
    name = models.CharField(
        verbose_name=_("name"),
        max_length=31,
        unique=True,
    )

    class Meta:
        verbose_name = _("transaction category")
        verbose_name_plural = _("transaction categories")

    def __str__(self):
        return str(self.name)


class TransactionTemplate(models.Model):
    """
    Defined a recurrent transaction

    associated to selling something (a burger, a beer, ...)
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        unique=True,
        error_messages={'unique':_("A template with this name already exist")},
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
    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.PROTECT,
        verbose_name=_('type'),
        max_length=31,
    )
    display = models.BooleanField(
        default = True,
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=255,
    )

    class Meta:
        verbose_name = _("transaction template")
        verbose_name_plural = _("transaction templates")

    def get_absolute_url(self):
        return reverse('note:template_update', args=(self.pk, ))


class TransactionType(models.Model):
    """
    Defined a recurrent transaction category

     Example: food, softs, ...
     """
    name = models.CharField(
        verbose_name=_("name"),
        max_length=31,
        unique=True,
    )

    class Meta:
        verbose_name = _("transaction type")
        verbose_name_plural = _("transaction types")

    def __str__(self):
        return str(self.name)


class Transaction(models.Model):
    """
    General transaction between two :model:`note.Note`

    amount is store in centimes of currency, making it a  positive integer
    value. (from someone to someone else)

    TODO: Ensure source != destination.
    """

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
    amount = models.PositiveIntegerField(verbose_name=_('amount'), )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
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

    @property
    def total(self):
        return self.amount * self.quantity


class MembershipTransaction(Transaction):
    """
    Special type of :model:`note.Transaction` associated to a :model:`member.Membership`.

    """

    membership = models.OneToOneField(
        'member.Membership',
        on_delete=models.PROTECT,
        related_name='transaction',
    )

    class Meta:
        verbose_name = _("membership transaction")
        verbose_name_plural = _("membership transactions")
