# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """
    An user profile

    We do not want to patch the Django Contrib :model:`auth.User`model;
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
        indexes = [models.Index(fields=['user'])]

    def get_absolute_url(self):
        return reverse('user_detail', args=(self.pk,))


class Club(models.Model):
    """
    A club is a group of people, whose membership is handle by their
    :model:`member.Membership`, and gives access to right defined by a :model:`member.Role`.
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

    def get_absolute_url(self):
        return reverse_lazy('member:club_detail', args=(self.pk,))


class Role(models.Model):
    """
    Role that an :model:`auth.User` can have in a :model:`member.Club`

    TODO: Integrate the right management, and create some standard Roles at the
    creation of the club.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return str(self.name)


class Membership(models.Model):
    """
    Register the membership of a user to a club, including roles and membership duration.

    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
    )
    roles = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
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
        indexes = [models.Index(fields=['user'])]

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(instance, created, **_kwargs):
#     """
#     Hook to save an user profile when an user is updated
#     """
#     if created:
#         Profile.objects.create(user=instance)
#     instance.profile.save()
