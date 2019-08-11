# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ActivityType(models.Model):
    """
    Type of Activity, (e.g "Pot", "Soirée Club") and associated properties
    """
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

    class Meta:
        verbose_name = _("activity type")
        verbose_name_plural = _("activity types")

    def __str__(self):
        return self.name


class Activity(models.Model):
    """
    An IRL event organized by a club for others.
    """
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

    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")


class Guest(models.Model):
    """
    People who are not current members of any clubs, and invited by someone who is a current member.
    """
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

    class Meta:
        verbose_name = _("guest")
        verbose_name_plural = _("guests")
