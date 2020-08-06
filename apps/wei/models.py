# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from member.models import Club, Membership
from note.models import MembershipTransaction
from permission.models import Role


class WEIClub(Club):
    """
    The WEI is a club. Register to the WEI is equivalent than be member of the club.
    """
    year = models.PositiveIntegerField(
        unique=True,
        default=date.today().year,
        verbose_name=_("year"),
    )

    date_start = models.DateField(
        verbose_name=_("date start"),
    )

    date_end = models.DateField(
        verbose_name=_("date end"),
    )

    @property
    def is_current_wei(self):
        """
        We consider that this is the current WEI iff there is no future WEI planned.
        """
        return not WEIClub.objects.filter(date_start__gt=self.date_start).exists()

    def update_membership_dates(self):
        """
        We can't join the WEI next years.
        """
        return

    class Meta:
        verbose_name = _("WEI")
        verbose_name_plural = _("WEI")


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

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("description"),
    )

    information_json = models.TextField(
        default="{}",
        verbose_name=_("survey information"),
        help_text=_("Information about the survey for new members, encoded in JSON"),
    )

    @property
    def information(self):
        """
        The information about the survey for new members are stored in a dictionary that can evolve following the years.
         The dictionary is stored as a JSON string.
        """
        return json.loads(self.information_json)

    @information.setter
    def information(self, information):
        """
        Store information as a JSON string
        """
        self.information_json = json.dumps(information)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Bus")
        verbose_name_plural = _("Buses")
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
        verbose_name=_("name"),
    )

    color = models.PositiveIntegerField(  # Use a color picker to get the hexa code
        verbose_name=_("color"),
        help_text=_("The color of the T-Shirt, stored with its number equivalent"),
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("description"),
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

    class Meta:
        verbose_name = _("WEI Role")
        verbose_name_plural = _("WEI Roles")


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

    soge_credit = models.BooleanField(
        default=False,
        verbose_name=_("Credit from Société générale"),
    )

    caution_check = models.BooleanField(
        default=False,
        verbose_name=_("Caution check given")
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

    clothing_cut = models.CharField(
        max_length=16,
        choices=(
            ('male', _("Male")),
            ('female', _("Female")),
        ),
        verbose_name=_("clothing cut"),
    )

    clothing_size = models.CharField(
        max_length=4,
        choices=(
            ('XS', "XS"),
            ('S', "S"),
            ('M', "M"),
            ('L', "L"),
            ('XL', "XL"),
            ('XXL', "XXL"),
        ),
        verbose_name=_("clothing size"),
    )

    health_issues = models.TextField(
        blank=True,
        default="",
        verbose_name=_("health issues"),
    )

    emergency_contact_name = models.CharField(
        max_length=255,
        verbose_name=_("emergency contact name"),
    )

    emergency_contact_phone = PhoneNumberField(
        max_length=32,
        verbose_name=_("emergency contact phone"),
    )

    ml_events_registration = models.BooleanField(
        default=False,
        verbose_name=_("Register on the mailing list to stay informed of the events of the campus (1 mail/week)"),
    )

    ml_sport_registration = models.BooleanField(
        default=False,
        verbose_name=_("Register on the mailing list to stay informed of the sport events of the campus (1 mail/week)"),
    )

    ml_art_registration = models.BooleanField(
        default=False,
        verbose_name=_("Register on the mailing list to stay informed of the art events of the campus (1 mail/week)"),
    )

    first_year = models.BooleanField(
        default=False,
        verbose_name=_("first year"),
        help_text=_("Tells if the user is new in the school.")
    )

    information_json = models.TextField(
        default="{}",
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
    def is_validated(self):
        try:
            return self.membership is not None
        except AttributeError:
            return False

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
        related_name="memberships",
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

    class Meta:
        verbose_name = _("WEI membership")
        verbose_name_plural = _("WEI memberships")

    def make_transaction(self):
        """
        Create Membership transaction associated to this membership.
        """
        if not self.fee or MembershipTransaction.objects.filter(membership=self).exists():
            return

        if self.fee:
            transaction = MembershipTransaction(
                membership=self,
                source=self.user.note,
                destination=self.club.note,
                quantity=1,
                amount=self.fee,
                reason="Adhésion WEI " + self.club.name,
                valid=not self.registration.soge_credit  # Soge transactions are by default invalidated
            )
            transaction._force_save = True
            transaction.save(force_insert=True)

            if self.registration.soge_credit and "treasury" in settings.INSTALLED_APPS:
                # If the soge pays, then the transaction is unvalidated in a first time, then submitted for control
                # to treasurers.
                transaction.refresh_from_db()
                from treasury.models import SogeCredit
                soge_credit = SogeCredit.objects.get_or_create(user=self.user)[0]
                soge_credit.refresh_from_db()
                transaction.save()
                soge_credit.transactions.add(transaction)
                soge_credit.save()
