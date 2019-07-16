# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Alias(models.Model):
    """
    A alias labels a Note instance, only for user and clubs
    """
    alias = models.TextField(
        "alias",
        unique=True,
        blank=False,
        null=False,
    )

    # Owner can be linked to an user note or a club note
    limit = models.Q(app_label="note", model="NoteUser") | models.Q(app_label="note", model="NoteClub")
    owner_id = models.PositiveIntegerField()
    owner_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit
    )
    owner = GenericForeignKey('owner_type', 'owner_id')


class Note(models.Model):
    """
    An abstract model, use to add transactions capabilities to a user
    """
    balance = models.DecimalField(
        verbose_name=_('account balance'),
        help_text=_("money credited for this instance"),
        decimal_places=2,  # Limit to centimes
        max_digits=8,  # Limit to 999999,99€
        default=0,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active')
    )

    class Meta:
        abstract = True


class NoteUser(Note):
    """
    A Note associated to an User
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("one's note")
        verbose_name_plural = _("users note")


class NoteSpec(Note):
    """
    A Note for special account, where real money enter or leave the system
    """
    account_type = models.CharField(
        max_length=2,
        choices=(
            ("CH", _("bank check")),
            ("CB", _("credit card")),
            ("VB", _("bank transfer")),
            ("CA", _("cash")),
            ("RB", _("refund")),
        ),
        unique=True,
    )


class NoteClub(Note):
    # to be added
    pass
