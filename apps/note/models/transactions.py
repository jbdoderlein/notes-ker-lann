# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from .notes import Note, NoteClub, NoteSpecial

"""
Defines transactions
"""


class TemplateCategory(models.Model):
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
        error_messages={'unique': _("A template with this name already exist")},
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
        TemplateCategory,
        on_delete=models.PROTECT,
        verbose_name=_('type'),
        max_length=31,
    )
    display = models.BooleanField(
        default=True,
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = _("transaction template")
        verbose_name_plural = _("transaction templates")

    def get_absolute_url(self):
        return reverse('note:template_update', args=(self.pk,))


class Transaction(PolymorphicModel):
    """
    General transaction between two :model:`note.Note`

    amount is store in centimes of currency, making it a  positive integer
    value. (from someone to someone else)
    """

    source = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('source'),
    )

    source_alias = models.CharField(
        max_length=255,
        default="",  # Will be remplaced by the name of the note on save
        verbose_name=_('used alias'),
    )

    destination = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('destination'),
    )

    destination_alias = models.CharField(
        max_length=255,
        default="",  # Will be remplaced by the name of the note on save
        verbose_name=_('used alias'),
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

    reason = models.CharField(
        verbose_name=_('reason'),
        max_length=255,
    )

    valid = models.BooleanField(
        verbose_name=_('valid'),
        default=True,
    )

    invalidity_reason = models.CharField(
        verbose_name=_('invalidity reason'),
        max_length=255,
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['source']),
            models.Index(fields=['destination']),
        ]

    def save(self, *args, **kwargs):
        """
        When saving, also transfer money between two notes
        """

        # If the aliases are not entered, we assume that the used alias is the name of the note
        if not self.source_alias:
            self.source_alias = str(self.source)

        if not self.destination_alias:
            self.destination_alias = str(self.destination)

        if self.source.pk == self.destination.pk:
            # When source == destination, no money is transfered
            super().save(*args, **kwargs)
            return

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

            # When a transaction is declared valid, we ensure that the invalidity reason is null, if it was
            # previously invalid
            self.invalidity_reason = None

        # We save first the transaction, in case of the user has no right to transfer money
        super().save(*args, **kwargs)

        # Save notes
        self.source.save()
        self.destination.save()

    @property
    def total(self):
        return self.amount * self.quantity

    @property
    def type(self):
        return _('Transfer')


class RecurrentTransaction(Transaction):
    """
    Special type of :model:`note.Transaction` associated to a :model:`note.TransactionTemplate`.
    """

    template = models.ForeignKey(
        TransactionTemplate,
        null=True,
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        TemplateCategory,
        on_delete=models.PROTECT,
    )

    @property
    def type(self):
        return _('Template')


class SpecialTransaction(Transaction):
    """
    Special type of :model:`note.Transaction` associated to transactions with special notes
    """

    last_name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name=_("first_name"),
    )

    bank = models.CharField(
        max_length=255,
        verbose_name=_("bank"),
        blank=True,
    )

    @property
    def type(self):
        return _('Credit') if isinstance(self.source, NoteSpecial) else _("Debit")


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

    @property
    def type(self):
        return _('membership transaction')
