# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

"""
Defines each note types
"""


class Note(models.Model):
    """
    An model, use to add transactions capabilities

    We do not use an abstract model to simplify the transfer between two notes.
    """
    balance = models.IntegerField(
        verbose_name=_('account balance'),
        help_text=_('in centimes, money credited for this instance'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this note should be treated as active. '
            'Unselect this instead of deleting notes.'
        ),
    )

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")


class NoteUser(Note):
    """
    A Note associated to an User
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='note',
    )

    class Meta:
        verbose_name = _("one's note")
        verbose_name_plural = _("users note")


class NoteClub(Note):
    """
    A Note associated to a Club
    """
    club = models.OneToOneField(
        'member.Club',
        on_delete=models.PROTECT,
        related_name='note',
    )

    class Meta:
        verbose_name = _("club note")
        verbose_name_plural = _("clubs notes")


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


class Alias(models.Model):
    """
    An alias labels a Note instance, only for user and clubs
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        unique=True,
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _("alias")
        verbose_name_plural = _("aliases")
