# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
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
        return _("%(user)s's note") % {'user': str(self.user)}

    def save(self, *args, **kwargs):
        """
        When saving, also create an alias
        TODO: check availability of alias
        TODO: remove old alias
        """
        created = self.pk is None
        if created:
            alias = Alias.objects.create(name=str(self.user), note=self)
            alias.save()

        super().save(*args, **kwargs)


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
        return _("Note for %(club)s club") % {'club': str(self.club)}

    def save(self, *args, **kwargs):
        """
        When saving, also create an alias
        TODO: check availability of alias
        TODO: remove old alias
        """
        created = self.pk is None
        if created:
            alias = Alias.objects.create(name=str(self.club), note=self)
            alias.save()

        super().save(*args, **kwargs)


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

    def save(self, *args, **kwargs):
        """
        When saving, also create an alias
        TODO: check availability of alias
        TODO: remove old alias
        """
        created = self.pk is None
        if created:
            alias = Alias.objects.create(name=str(self.club), note=self)
            alias.save()

        super().save(*args, **kwargs)


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

    def __str__(self):
        return self.name
