# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import unicodedata

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

"""
Defines each note types
"""


class Note(PolymorphicModel):
    """
    An model, use to add transactions capabilities
    """
    balance = models.IntegerField(
        verbose_name=_('account balance'),
        help_text=_('in centimes, money credited for this instance'),
        default=0,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this note should be treated as active. '
            'Unselect this instead of deleting notes.'
        ),
    )
    display_image = models.ImageField(
        verbose_name=_('display image'),
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")

    def pretty(self):
        """
        :return: Pretty name of this note
        """
        return str(self)

    pretty.short_description = _('Note')

    def save(self, *args, **kwargs):
        """
        Save note with it's alias (called in polymorphic children)
        """
        aliases = Alias.objects.filter(name=str(self))
        if aliases.exists():
            # Alias exists, so check if it is linked to this note
            if aliases.first().note != self:
                raise ValidationError(_('This alias is already taken.'))

            # Save note
            super().save(*args, **kwargs)
        else:
            # Alias does not exist yet, so check if it can exist
            a = Alias(name=str(self))
            a.clean()

            # Save note and alias
            super().save(*args, **kwargs)
            a.note = self
            a.save(force_insert=True)

    def clean(self, *args, **kwargs):
        """
        Verify alias (simulate save)
        """
        aliases = Alias.objects.filter(name=str(self))
        if aliases.exists():
            # Alias exists, so check if it is linked to this note
            if aliases.first().note != self:
                raise ValidationError(_('This alias is already taken.'))
        else:
            # Alias does not exist yet, so check if it can exist
            a = Alias(name=str(self))
            a.clean()


class NoteUser(Note):
    """
    A Note associated to an User
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='note',
        verbose_name=_('user'),
    )

    class Meta:
        verbose_name = _("one's note")
        verbose_name_plural = _("users note")

    def __str__(self):
        return str(self.user)

    def pretty(self):
        return _("%(user)s's note") % {'user': str(self.user)}


class NoteClub(Note):
    """
    A Note associated to a Club
    """
    club = models.OneToOneField(
        'member.Club',
        on_delete=models.PROTECT,
        related_name='note',
        verbose_name=_('club'),
    )

    class Meta:
        verbose_name = _("club note")
        verbose_name_plural = _("clubs notes")

    def __str__(self):
        return str(self.club)

    def pretty(self):
        return _("Note for %(club)s club") % {'club': str(self.club)}


class NoteSpecial(Note):
    """
    A Note for special account, where real money enter or leave the system
    - bank check
    - credit card
    - bank transfer
    - cash
    - refund
    """
    special_type = models.CharField(
        verbose_name=_('type'),
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = _("special note")
        verbose_name_plural = _("special notes")

    def __str__(self):
        return self.special_type


class Alias(models.Model):
    """
    An alias labels a Note instance, only for user and clubs
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                regex=settings.ALIAS_VALIDATOR_REGEX,
                message=_('Invalid alias')
            )
        ] if settings.ALIAS_VALIDATOR_REGEX else []
    )
    normalized_name = models.CharField(
        max_length=255,
        unique=True,
        default='',
        editable=False
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _("alias")
        verbose_name_plural = _("aliases")

    def __str__(self):
        return self.name

    @staticmethod
    def normalize(string):
        """
        Normalizes a string: removes most diacritics and does casefolding
        """
        return ''.join(
            char
            for char in unicodedata.normalize('NFKD', string.casefold())
            if all(not unicodedata.category(char).startswith(cat)
                   for cat in {'M', 'P', 'Z', 'C'})
        )

    def save(self, *args, **kwargs):
        """
        Handle normalized_name
        """
        self.normalized_name = Alias.normalize(self.name)
        if len(self.normalized_name) < 256:
            super().save(*args, **kwargs)

    def clean(self):
        normalized_name = Alias.normalize(self.name)
        if len(normalized_name) >= 255:
            raise ValidationError(_('Alias too long.'))
        try:
            if self != Alias.objects.get(normalized_name=normalized_name):
                raise ValidationError(_('An alias with a similar name '
                                        'already exists.'))
        except Alias.DoesNotExist:
            pass
