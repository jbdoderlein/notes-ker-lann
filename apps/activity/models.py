# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from datetime import timedelta
from threading import Thread

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from note.models import NoteUser, Transaction
from rest_framework.exceptions import ValidationError


class ActivityType(models.Model):
    """
    Type of Activity, (e.g "Pot", "Soirée Club") and associated properties.

    Activity Type are used as a search field for Activity, and determine how
    some rules about the activity:
     - Can people be invited
     - What is the entrance fee.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )

    manage_entries = models.BooleanField(
        verbose_name=_('manage entries'),
        help_text=_('Enable the support of entries for this activity.'),
        default=False,
    )

    can_invite = models.BooleanField(
        verbose_name=_('can invite'),
        default=False,
    )

    guest_entry_fee = models.PositiveIntegerField(
        verbose_name=_('guest entry fee'),
        default=0,
    )

    class Meta:
        verbose_name = _("activity type")
        verbose_name_plural = _("activity types")

    def __str__(self):
        return self.name


class Activity(models.Model):
    """
    An IRL event organized by a club for other club.

    By default the invited clubs should be the Club containing all the active accounts.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )

    description = models.TextField(
        verbose_name=_('description'),
    )

    location = models.CharField(
        verbose_name=_('location'),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Place where the activity is organized, eg. Kfet."),
    )

    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('type'),
    )

    creater = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("user"),
    )

    organizer = models.ForeignKey(
        'member.Club',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('organizer'),
        help_text=_("Club that organizes the activity. The entry fees will go to this club."),
    )

    attendees_club = models.ForeignKey(
        'member.Club',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('attendees club'),
        help_text=_("Club that is authorized to join the activity. Mostly the Kfet club."),
    )

    date_start = models.DateTimeField(
        verbose_name=_('start date'),
    )

    date_end = models.DateTimeField(
        verbose_name=_('end date'),
    )

    valid = models.BooleanField(
        default=False,
        verbose_name=_('valid'),
    )

    open = models.BooleanField(
        default=False,
        verbose_name=_('open'),
    )

    def save(self, *args, **kwargs):
        """
        Update the activity wiki page each time the activity is updated (validation, change description, ...)
        """
        if self.date_end < self.date_start:
            raise ValidationError(_("The end date must be after the start date."))

        ret = super().save(*args, **kwargs)
        if not settings.DEBUG and self.pk and "scripts" in settings.INSTALLED_APPS:
            def refresh_activities():
                from scripts.management.commands.refresh_activities import Command as RefreshActivitiesCommand
                # Consider that we can update the wiki iff the WIKI_PASSWORD env var is not empty
                RefreshActivitiesCommand.refresh_human_readable_wiki_page("Modification de l'activité " + self.name,
                                                                          False, os.getenv("WIKI_PASSWORD"))
                RefreshActivitiesCommand.refresh_raw_wiki_page("Modification de l'activité " + self.name,
                                                               False, os.getenv("WIKI_PASSWORD"))
            Thread(daemon=True, target=refresh_activities).start()\
                if settings.DATABASES["default"]["ENGINE"] == 'django.db.backends.postgresql' else refresh_activities()
        return ret

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        unique_together = ("name", "date_start", "date_end",)


class Entry(models.Model):
    """
    Register the entry of someone:
    - a member with a :model:`note.NoteUser`
    - or a :model:`activity.Guest`
    In the case of a Guest Entry, the inviter note is also save.
    """
    activity = models.ForeignKey(
        Activity,
        on_delete=models.PROTECT,
        related_name="entries",
        verbose_name=_("activity"),
    )

    time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("entry time"),
    )

    note = models.ForeignKey(
        NoteUser,
        on_delete=models.PROTECT,
        verbose_name=_("note"),
    )

    guest = models.OneToOneField(
        'activity.Guest',
        on_delete=models.PROTECT,
        null=True,
    )

    class Meta:
        unique_together = (('activity', 'note', 'guest', ), )
        verbose_name = _("entry")
        verbose_name_plural = _("entries")

    def save(self, *args, **kwargs):

        qs = Entry.objects.filter(~Q(pk=self.pk), activity=self.activity, note=self.note, guest=self.guest)
        if qs.exists():
            raise ValidationError(_("Already entered on ") + _("{:%Y-%m-%d %H:%M:%S}").format(qs.get().time, ))

        if self.guest:
            self.note = self.guest.inviter

        insert = not self.pk
        if insert:
            if self.note.balance < 0:
                raise ValidationError(_("The balance is negative."))

        ret = super().save(*args, **kwargs)

        if insert and self.guest:
            GuestTransaction.objects.create(
                source=self.note,
                destination=self.activity.organizer.note,
                quantity=1,
                amount=self.activity.activity_type.guest_entry_fee,
                reason="Invitation " + self.activity.name + " " + self.guest.first_name + " " + self.guest.last_name,
                valid=True,
                entry=self,
            ).save()

        return ret


class Guest(models.Model):
    """
    People who are not current members of any clubs, and are invited by someone who is a current member.
    """
    activity = models.ForeignKey(
        Activity,
        on_delete=models.PROTECT,
        related_name='+',
    )

    last_name = models.CharField(
        max_length=255,
        verbose_name=_("last name"),
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name=_("first name"),
    )

    inviter = models.ForeignKey(
        NoteUser,
        on_delete=models.PROTECT,
        related_name='guests',
        verbose_name=_("inviter"),
    )

    @property
    def has_entry(self):
        try:
            if self.entry:
                return True
            return False
        except AttributeError:
            return False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        one_year = timedelta(days=365)

        if not force_insert:
            if timezone.now() > timezone.localtime(self.activity.date_start):
                raise ValidationError(_("You can't invite someone once the activity is started."))

            if not self.activity.valid:
                raise ValidationError(_("This activity is not validated yet."))

            qs = Guest.objects.filter(
                first_name__iexact=self.first_name,
                last_name__iexact=self.last_name,
                activity__date_start__gte=self.activity.date_start - one_year,
            )
            if qs.filter(entry__isnull=False).count() >= 5:
                raise ValidationError(_("This person has been already invited 5 times this year."))

            qs = qs.filter(activity=self.activity)
            if qs.exists():
                raise ValidationError(_("This person is already invited."))

            qs = Guest.objects.filter(inviter=self.inviter, activity=self.activity)
            if qs.count() >= 3:
                raise ValidationError(_("You can't invite more than 3 people to this activity."))

        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        verbose_name = _("guest")
        verbose_name_plural = _("guests")
        unique_together = ("activity", "last_name", "first_name", )


class GuestTransaction(Transaction):
    entry = models.OneToOneField(
        Entry,
        on_delete=models.PROTECT,
    )

    @property
    def type(self):
        return _('Invitation')
