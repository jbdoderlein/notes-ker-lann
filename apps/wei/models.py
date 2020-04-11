# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from note.models import NoteSpecial


class WEI(models.Model):
    """
    Store WEI information
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("name"),
    )

    year = models.PositiveIntegerField(
        unique=True,
        verbose_name=_("year"),
    )

    start = models.DateField(
        verbose_name=_("start date"),
    )

    end = models.DateField(
        verbose_name=_("end date"),
    )

    price_paid = models.PositiveIntegerField(
        verbose_name=_("Price for paid students"),
    )

    price_unpaid = models.PositiveIntegerField(
        verbose_name=_("Price for unpaid students"),
    )

    email = models.EmailField(
        verbose_name=_("contact email"),
    )

    registrations_open = models.BooleanField(
        verbose_name=_("registrations open"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("WEI")
        verbose_name_plural = _("WEI")


class Bus(models.Model):
    """
    The best bus for the best WEI
    """
    wei = models.ForeignKey(
        WEI,
        on_delete=models.PROTECT,
        related_name="buses",
        verbose_name=_("WEI"),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('wei', 'name',)


class BusTeam(models.Model):
    """
    A bus has multiple teams
    """
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name="teams",
        verbose_name=_("bus"),
    )

    name = models.CharField(
        max_length=255,
    )

    color = models.PositiveIntegerField(  # Use a color picker to get the hexa code
        verbose_name=_("color"),
        help_text=_("The color of the T-Shirt, stored with its number equivalent"),
    )

    def __str__(self):
        return self.name + " (" + str(self.bus) + ")"

    class Meta:
        unique_together = ('bus', 'name',)
        verbose_name = _("Bus team")
        verbose_name_plural = _("Bus teams")


class WEIRole(models.Model):
    """
    A Role for the WEI can be bus chief, team chief, free electron, ...
    """
    name = models.CharField(
        max_length=255,
        unique=True,
    )


class WEIUser(models.Model):
    """
    Store personal data that can be useful for the WEI.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="wei",
        verbose_name=_("user"),
    )

    wei = models.ForeignKey(
        WEI,
        on_delete=models.PROTECT,
        related_name="users",
        verbose_name=_("WEI"),
    )

    role = models.ForeignKey(
        WEIRole,
        on_delete=models.PROTECT,
        verbose_name=_("role"),
    )

    birth_date = models.DateField(
        verbose_name=_("birth date"),
    )

    gender = models.CharField(
        max_length=16,
        choices=(
            ('male', _("Male")),
            ('female', _("Female")),
            ('nonbinary', _("Non binary")),
        ),
        verbose_name=_("gender"),
    )

    health_issues = models.TextField(
        verbose_name=_("health issues"),
    )

    emergency_contact_name = models.CharField(
        max_length=255,
        verbose_name=_("emergency contact name"),
    )

    emergency_contact_phone = models.CharField(
        max_length=32,
        verbose_name=_("emergency contact phone"),
    )

    payment_method = models.ForeignKey(
        NoteSpecial,
        on_delete=models.PROTECT,
        null=True,  # null = no credit, paid with note
        related_name="+",
        verbose_name=_("payment method"),
    )

    soge_credit = models.BooleanField(
        verbose_name=_("Credit from Société générale"),
    )

    ml_events_registation = models.BooleanField(
        verbose_name=_("Register on the mailing list to stay informed of the events of the campus (1 mail/week)"),
    )

    ml_sport_registation = models.BooleanField(
        verbose_name=_("Register on the mailing list to stay informed of the sport events of the campus (1 mail/week)"),
    )

    ml_art_registation = models.BooleanField(
        verbose_name=_("Register on the mailing list to stay informed of the art events of the campus (1 mail/week)"),
    )

    team = models.ForeignKey(
        BusTeam,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
        verbose_name=_("team"),
    )

    bus_choice1 = models.ForeignKey(
        Bus,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("bus choice 1"),
    )

    bus_choice2 = models.ForeignKey(
        Bus,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name=_("bus choice 2"),
    )

    bus_choice3 = models.ForeignKey(
        Bus,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name=_("bus choice 3"),
    )

    asked_roles = models.ManyToManyField(
        WEIRole,
        related_name="+",
        verbose_name=_("asked roles"),
    )

    def __str__(self):
        return str(self.user)

    class Meta:
        unique_together = ('user', 'wei',)
        verbose_name = _("WEI User")
        verbose_name_plural = _("WEI Users")
