# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2016-2019 by BDE
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.models import User
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
        max_length=255,
        verbose_name=_('phone number'),
    )
    section = models.CharField(
        max_length=255,
        verbose_name=_('section'),
        help_text=_('e.g. "1A0", "9A♥", "SAPHIRE"'),
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profile')

    def __str__(self):
        return self.user.get_username()


class MembershipFee(models.Model):
    """
    User can become member by paying a membership fee
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    date = models.DateField(
        max_length=255,
        verbose_name=_('date'),
    )
    amount = models.DecimalField(
        max_digits=5, # Max 999.99 €
        decimal_places=2,
        verbose_name=_('amount'),
    )

    class Meta:
        verbose_name = _('membership fee')
        verbose_name_plural = _('membership fees')

    def __str__(self):
        return self.user.get_username()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **_kwargs):
    """
    Hook to save an user profile when an user is updated
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
