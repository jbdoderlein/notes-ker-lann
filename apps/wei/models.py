# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
import json

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from member.models import Role, Club, Membership
from note.models import NoteSpecial


class WEIClub(Club):
    """
    """
    year = models.PositiveIntegerField(
        unique=True,
        verbose_name=_("year"),
    )

    def update_membership_dates(self):
        """
        We can't join the WEI next years.
        """
        return


class Bus(models.Model):
    """
    The best bus for the best WEI
    """
    wei = models.ForeignKey(
        WEIClub,
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


class WEIRole(Role):
    """
    A Role for the WEI can be bus chief, team chief, free electron, ...
    """
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name=_("bus"),
    )


class WEIRegistration(models.Model):
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
        WEIClub,
        on_delete=models.PROTECT,
        related_name="users",
        verbose_name=_("WEI"),
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

    ml_events_registration = models.BooleanField(
        verbose_name=_("Register on the mailing list to stay informed of the events of the campus (1 mail/week)"),
    )

    ml_sport_registration = models.BooleanField(
        verbose_name=_("Register on the mailing list to stay informed of the sport events of the campus (1 mail/week)"),
    )

    ml_art_registration = models.BooleanField(
        verbose_name=_("Register on the mailing list to stay informed of the art events of the campus (1 mail/week)"),
    )

    information_json = models.TextField(
        verbose_name=_("registration information"),
        help_text=_("Information about the registration (buses for old members, survey fot the new members), "
                    "encoded in JSON"),
    )

    @property
    def information(self):
        """
        The information about the registration (the survey for the new members, the bus for the older members, ...)
        are stored in a dictionary that can evolve following the years. The dictionary is stored as a JSON string.
        """
        return json.loads(self.information_json)

    @information.setter
    def information(self, information):
        """
        Store information as a JSON string
        """
        self.information_json = json.dumps(information)

    @property
    def is_1A(self):
        """
        We assume that a user is a new member if it not fully registered yet.
        """
        return not self.user.profile.registration_valid

    def __str__(self):
        return str(self.user)

    class Meta:
        unique_together = ('user', 'wei',)
        verbose_name = _("WEI User")
        verbose_name_plural = _("WEI Users")


class WEIMembership(Membership):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        verbose_name=_("bus"),
    )

    team = models.ForeignKey(
        BusTeam,
        on_delete=models.PROTECT,
        related_name="memberships",
        null=True,
        blank=True,
        default=None,
        verbose_name=_("team"),
    )

    registration = models.OneToOneField(
        WEIRegistration,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name="membership",
        verbose_name=_("WEI registration"),
    )

