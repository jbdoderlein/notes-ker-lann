# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ActivityType(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )
    can_invite = models.BooleanField(
        verbose_name=_('can invite'),
    )
    guest_entry_fee = models.PositiveIntegerField(
        verbose_name=_('guest entry fee'),
    )


class Activity(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('type'),
    )
    organizer = models.ForeignKey(
        'member.Club',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('organizer'),
    )
    attendees_club = models.ForeignKey(
        'member.Club',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('attendees club'),
    )
    date_start = models.DateTimeField(
        verbose_name=_('start date'),
    )
    date_end = models.DateTimeField(
        verbose_name=_('end date'),
    )


class Guest(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.PROTECT,
        related_name='+',
    )
    name = models.CharField(
        max_length=255,
    )
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
    )
    entry = models.DateTimeField(
        null=True,
    )
    entry_transaction = models.ForeignKey(
        'note.Transaction',
        on_delete=models.PROTECT,
    )
