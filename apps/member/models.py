# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """
    An user profile

    We do not want to patch the Django Contrib Auth User class
    so this model add an user profile with additional information.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    phone_number = models.CharField(
        verbose_name=_('phone number'),
        max_length=50,
        blank=True,
        null=True,
    )
    section = models.CharField(
        verbose_name=_('section'),
        help_text=_('e.g. "1A0", "9A♥", "SAPHIRE"'),
        max_length=255,
        blank=True,
        null=True,
    )
    address = models.CharField(
        verbose_name=_('address'),
        max_length=255,
        blank=True,
        null=True,
    )
    paid = models.BooleanField(
        verbose_name=_("paid"),
        default=False,
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profile')


class Club(models.Model):
    """
    A student club
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        unique=True,
    )
    email = models.EmailField(
        verbose_name=_('email'),
    )

    # Memberships
    membership_fee = models.PositiveIntegerField(
        verbose_name=_('membership fee'),
    )
    membership_duration = models.DurationField(
        null=True,
        verbose_name=_('membership duration'),
        help_text=_('The longest time a membership can last '
                    '(NULL = infinite).'),
    )
    membership_start = models.DurationField(
        null=True,
        verbose_name=_('membership start'),
        help_text=_('How long after January 1st the members can renew '
                    'their membership.'),
    )
    membership_end = models.DurationField(
        null=True,
        verbose_name=_('membership end'),
        help_text=_('How long the membership can last after January 1st '
                    'of the next year after members can renew their '
                    'membership.'),
    )

    class Meta:
        verbose_name = _("club")
        verbose_name_plural = _("clubs")

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Role that an user can have in a club
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')


class Membership(models.Model):
    """
    Register the membership of a user to a club, including roles and membership duration.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.PROTECT
    )
    roles = models.ForeignKey(
        Role,
        on_delete=models.PROTECT
    )
    date_start = models.DateField(
        verbose_name=_('membership starts on'),
    )
    date_end = models.DateField(
        verbose_name=_('membership ends on'),
        null=True,
    )
    fee = models.PositiveIntegerField(
        verbose_name=_('fee'),
    )

    class Meta:
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(instance, created, **_kwargs):
#     """
#     Hook to save an user profile when an user is updated
#     """
#     if created:
#         Profile.objects.create(user=instance)
#     instance.profile.save()
