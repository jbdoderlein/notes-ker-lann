# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from .notes import Note, NoteClub, NoteSpecial
from ..templatetags.pretty_money import pretty_money

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
    )
    category = models.ForeignKey(
        TemplateCategory,
        on_delete=models.PROTECT,
        related_name='templates',
        verbose_name=_('type'),
        max_length=31,
    )

    display = models.BooleanField(
        default=True,
        verbose_name=_("display"),
    )

    highlighted = models.BooleanField(
        default=False,
        verbose_name=_("highlighted"),
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

    def __str__(self):
        return self.name


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
        default='',
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

    def validate(self):
        previous_source_balance = self.source.balance
        previous_dest_balance = self.destination.balance

        source_balance = self.source.balance
        dest_balance = self.destination.balance

        created = self.pk is None
        to_transfer = self.amount * self.quantity
        if not created:
            # Revert old transaction
            old_transaction = Transaction.objects.get(pk=self.pk)
            # Check that nothing important changed
            for field_name in ["source_id", "destination_id", "quantity", "amount"]:
                if getattr(self, field_name) != getattr(old_transaction, field_name):
                    raise ValidationError(_("You can't update the {field} on a Transaction. "
                                            "Please invalidate it and create one other.").format(field=field_name))

            if old_transaction.valid == self.valid:
                # Don't change anything
                return 0, 0
            if old_transaction.valid:
                source_balance += to_transfer
                dest_balance -= to_transfer

        if self.valid:
            source_balance -= to_transfer
            dest_balance += to_transfer

            # When a transaction is declared valid, we ensure that the invalidity reason is null, if it was
            # previously invalid
            self.invalidity_reason = ""

        if source_balance > 9223372036854775807 or source_balance < -9223372036854775808\
                or dest_balance > 9223372036854775807 or dest_balance < -9223372036854775808:
            raise ValidationError(_("The note balances must be between - 92 233 720 368 547 758.08 € "
                                    "and 92 233 720 368 547 758.07 €."))

        return source_balance - previous_source_balance, dest_balance - previous_dest_balance

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        When saving, also transfer money between two notes
        """
        if self.source.pk == self.destination.pk:
            # When source == destination, no money is transferred and no transaction is created
            return

        # We refresh the notes with the "select for update" tag to avoid concurrency issues
        self.source = Note.objects.filter(pk=self.source_id).select_for_update().get()
        self.destination = Note.objects.filter(pk=self.destination_id).select_for_update().get()

        # Check that the amounts stay between big integer bounds
        diff_source, diff_dest = self.validate()

        if not self.source.is_active or not self.destination.is_active:
            raise ValidationError(_("The transaction can't be saved since the source note "
                                    "or the destination note is not active."))

        # If the aliases are not entered, we assume that the used alias is the name of the note
        if not self.source_alias:
            self.source_alias = str(self.source)

        if not self.destination_alias:
            self.destination_alias = str(self.destination)

        # We save first the transaction, in case of the user has no right to transfer money
        super().save(*args, **kwargs)

        # Save notes
        self.source.balance += diff_source
        self.source._force_save = True
        self.source.save()
        self.destination.balance += diff_dest
        self.destination._force_save = True
        self.destination.save()

    @property
    def total(self):
        return self.amount * self.quantity

    @property
    def type(self):
        return _('Transfer')

    def __str__(self):
        return self.__class__.__name__ + " from " + str(self.source) + " to " + str(self.destination) + " of "\
            + pretty_money(self.quantity * self.amount) + ("" if self.valid else " invalid")


class RecurrentTransaction(Transaction):
    """
    Special type of :model:`note.Transaction` associated to a :model:`note.TransactionTemplate`.
    """

    template = models.ForeignKey(
        TransactionTemplate,
        on_delete=models.PROTECT,
    )

    def clean(self):
        if self.template.destination != self.destination:
            raise ValidationError(
                _("The destination of this transaction must equal to the destination of the template."))
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    @property
    def type(self):
        return _('Template')

    class Meta:
        verbose_name = _("recurrent transaction")
        verbose_name_plural = _("recurrent transactions")


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

    def is_credit(self):
        return isinstance(self.source, NoteSpecial)

    def is_debit(self):
        return isinstance(self.destination, NoteSpecial)

    def clean(self):
        # SpecialTransaction are only possible with NoteSpecial object
        if self.is_credit() == self.is_debit():
            raise(ValidationError(_("A special transaction is only possible between a"
                                    " Note associated to a payment method and a User or a Club")))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Special transaction")
        verbose_name_plural = _("Special transactions")


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
        return _('membership').capitalize()
