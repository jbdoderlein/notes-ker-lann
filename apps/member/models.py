# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from permission.models import Role
from registration.tokens import email_validation_token
from note.models import MembershipTransaction


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

    phone_number = PhoneNumberField(
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

    department = models.CharField(
        max_length=8,
        verbose_name=_("department"),
        choices=[
            ('A0', _("Informatics (A0)")),
            ('A1', _("Mathematics (A1)")),
            ('A2', _("Physics (A2)")),
            ("A'2", _("Applied physics (A'2)")),
            ('A''2', _("Chemistry (A''2)")),
            ('A3', _("Biology (A3)")),
            ('B1234', _("SAPHIRE (B1234)")),
            ('B1', _("Mechanics (B1)")),
            ('B2', _("Civil engineering (B2)")),
            ('B3', _("Mechanical engineering (B3)")),
            ('B4', _("EEA (B4)")),
            ('C', _("Design (C)")),
            ('D2', _("Economy-management (D2)")),
            ('D3', _("Social sciences (D3)")),
            ('E', _("English (E)")),
            ('EXT', _("External (EXT)")),
        ]
    )

    promotion = models.PositiveSmallIntegerField(
        null=True,
        default=datetime.date.today().year,
        verbose_name=_("promotion"),
        help_text=_("Year of entry to the school (None if not ENS student)"),
    )

    address = models.CharField(
        verbose_name=_('address'),
        max_length=255,
        blank=True,
        null=True,
    )

    paid = models.BooleanField(
        verbose_name=_("paid"),
        help_text=_("Tells if the user receive a salary."),
        default=False,
    )

    ml_events_registration = models.CharField(
        blank=True,
        null=True,
        default=None,
        max_length=2,
        choices=[
            (None, _("No")),
            ('fr', _("Yes (receive them in french)")),
            ('en', _("Yes (receive them in english)")),
        ],
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

    report_frequency = models.PositiveSmallIntegerField(
        verbose_name=_("report frequency (in days)"),
        default=0,
    )

    last_report = models.DateTimeField(
        verbose_name=_("last report date"),
        default=timezone.now,
    )

    email_confirmed = models.BooleanField(
        verbose_name=_("email confirmed"),
        default=False,
    )

    registration_valid = models.BooleanField(
        verbose_name=_("registration valid"),
        default=False,
    )

    @property
    def ens_year(self):
        """
        Number of years since the 1st august of the entry year, rounded up.
        """
        if self.promotion is None:
            return 0
        today = datetime.date.today()
        years = today.year - self.promotion
        if today.month >= 8:
            years += 1
        return years

    @property
    def section_generated(self):
        return str(self.ens_year) + self.department

    @property
    def soge(self):
        if "treasury" in settings.INSTALLED_APPS:
            from treasury.models import SogeCredit
            return SogeCredit.objects.filter(user=self.user, credit_transaction__isnull=False).exists()
        return False

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profile')
        indexes = [models.Index(fields=['user'])]

    def get_absolute_url(self):
        return reverse('member:user_detail', args=(self.user_id,))

    def __str__(self):
        return str(self.user)

    def send_email_validation_link(self):
        subject = "[Note Kfet] " + str(_("Activate your Note Kfet account"))
        token = email_validation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user_id))
        message = loader.render_to_string('registration/mails/email_validation_email.txt',
                                          {
                                              'user': self.user,
                                              'domain': os.getenv("NOTE_URL", "note.example.com"),
                                              'token': token,
                                              'uid': uid,
                                          })
        html = loader.render_to_string('registration/mails/email_validation_email.html',
                                       {
                                           'user': self.user,
                                           'domain': os.getenv("NOTE_URL", "note.example.com"),
                                           'token': token,
                                           'uid': uid,
                                       })
        self.user.email_user(subject, message, html_message=html)


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
    parent_club = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('parent club'),
    )

    # Memberships

    # When set to False, the membership system won't be used.
    # Useful to create notes for activities or departments.
    require_memberships = models.BooleanField(
        default=True,
        verbose_name=_("require memberships"),
        help_text=_("Uncheck if this club don't require memberships."),
    )

    membership_fee_paid = models.PositiveIntegerField(
        default=0,
        verbose_name=_('membership fee (paid students)'),
    )

    membership_fee_unpaid = models.PositiveIntegerField(
        default=0,
        verbose_name=_('membership fee (unpaid students)'),
    )

    membership_duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('membership duration'),
        help_text=_('The longest time (in days) a membership can last '
                    '(NULL = infinite).'),
    )

    membership_start = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('membership start'),
        help_text=_('Date from which the members can renew their membership.'),
    )

    membership_end = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('membership end'),
        help_text=_('Maximal date of a membership, after which members must renew it.'),
    )

    def update_membership_dates(self):
        """
        This function is called each time the club detail view is displayed.
        Update the year of the membership dates.
        """
        if not self.membership_start:
            return

        today = datetime.date.today()

        if (today - self.membership_start).days >= 365:
            self.membership_start = datetime.date(self.membership_start.year + 1,
                                                  self.membership_start.month, self.membership_start.day)
            self.membership_end = datetime.date(self.membership_end.year + 1,
                                                self.membership_end.month, self.membership_end.day)
            self._force_save = True
            self.save(force_update=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.require_memberships:
            self.membership_fee_paid = 0
            self.membership_fee_unpaid = 0
            self.membership_duration = None
            self.membership_start = None
            self.membership_end = None
        super().save(force_insert, force_update, update_fields)

    class Meta:
        verbose_name = _("club")
        verbose_name_plural = _("clubs")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('member:club_detail', args=(self.pk,))


class Membership(models.Model):
    """
    Register the membership of a user to a club, including roles and membership duration.

    """
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="memberships",
        verbose_name=_("user"),
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
        verbose_name=_("club"),
    )

    roles = models.ManyToManyField(
        "permission.Role",
        verbose_name=_("roles"),
    )

    date_start = models.DateField(
        default=datetime.date.today,
        verbose_name=_('membership starts on'),
    )

    date_end = models.DateField(
        verbose_name=_('membership ends on'),
        null=True,
    )

    fee = models.PositiveIntegerField(
        verbose_name=_('fee'),
    )

    @property
    def valid(self):
        """
        A membership is valid if today is between the start and the end date.
        """
        if self.date_end is not None:
            return self.date_start.toordinal() <= datetime.datetime.now().toordinal() < self.date_end.toordinal()
        else:
            return self.date_start.toordinal() <= datetime.datetime.now().toordinal()

    def renew(self):
        if not Membership.objects.filter(
                user=self.user,
                club=self.club,
                date_start__gte=self.club.membership_start,
        ).exists():
            # Membership is not renewed yet
            new_membership = Membership(
                user=self.user,
                club=self.club,
                date_start=max(self.date_end + datetime.timedelta(days=1), self.club.membership_start),
            )
            if hasattr(self, '_force_renew_parent') and self._force_renew_parent:
                new_membership._force_renew_parent = True
            if hasattr(self, '_soge') and self._soge:
                new_membership._soge = True
            if hasattr(self, '_force_save') and self._force_save:
                new_membership._force_save = True
            new_membership.save()
            new_membership.roles.set(self.roles.all())
            new_membership.save()

    def save(self, *args, **kwargs):
        """
        Calculate fee and end date before saving the membership and creating the transaction if needed.
        """
        created = not self.pk
        if not created:
            for role in self.roles.all():
                club = role.for_club
                if club is not None:
                    if club.pk != self.club_id:
                        raise ValidationError(_('The role {role} does not apply to the club {club}.')
                                              .format(role=role.name, club=club.name))
        else:
            if Membership.objects.filter(
                    user=self.user,
                    club=self.club,
                    date_start__lte=self.date_start,
                    date_end__gte=self.date_start,
            ).exists():
                raise ValidationError(_('User is already a member of the club'))

            if self.club.parent_club is not None:
                # Check that the user is already a member of the parent club if the membership is created
                if not Membership.objects.filter(
                    user=self.user,
                    club=self.club.parent_club,
                    date_start__gte=self.club.parent_club.membership_start,
                ).exists():
                    if hasattr(self, '_force_renew_parent') and self._force_renew_parent:
                        parent_membership = Membership.objects.filter(
                            user=self.user,
                            club=self.club.parent_club,
                        ).order_by("-date_start")
                        if parent_membership.exists():
                            # Renew the previous membership of the parent club
                            parent_membership = parent_membership.first()
                            parent_membership._force_renew_parent = True
                            if hasattr(self, '_soge'):
                                parent_membership._soge = True
                            if hasattr(self, '_force_save'):
                                parent_membership._force_save = True
                            parent_membership.renew()
                        else:
                            # Create a new membership in the parent club
                            parent_membership = Membership(
                                user=self.user,
                                club=self.club.parent_club,
                                date_start=self.date_start,
                            )
                            parent_membership._force_renew_parent = True
                            if hasattr(self, '_soge'):
                                parent_membership._soge = True
                            if hasattr(self, '_force_save'):
                                parent_membership._force_save = True
                            parent_membership.save()
                            parent_membership.refresh_from_db()

                            if self.club.parent_club.name == "BDE":
                                parent_membership.roles.set(
                                    Role.objects.filter(Q(name="Adhérent BDE") | Q(name="Membre de club")).all())
                            elif self.club.parent_club.name == "Kfet":
                                parent_membership.roles.set(
                                    Role.objects.filter(Q(name="Adhérent Kfet") | Q(name="Membre de club")).all())
                            else:
                                parent_membership.roles.set(Role.objects.filter(name="Membre de club").all())
                            parent_membership.save()
                    else:
                        raise ValidationError(_('User is not a member of the parent club')
                                              + ' ' + self.club.parent_club.name)

            self.fee = self.club.membership_fee_paid if self.user.profile.paid else self.club.membership_fee_unpaid

            self.date_end = self.date_start + datetime.timedelta(days=self.club.membership_duration) \
                if self.club.membership_duration is not None else self.date_start + datetime.timedelta(days=424242)
            if self.club.membership_end is not None and self.date_end > self.club.membership_end:
                self.date_end = self.club.membership_end

        super().save(*args, **kwargs)

        self.make_transaction()

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
                reason="Adhésion " + self.club.name,
            )
            transaction._force_save = True
            if hasattr(self, '_soge') and "treasury" in settings.INSTALLED_APPS\
                    and (self.club.name == "BDE" or self.club.name == "Kfet"
                         or ("wei" in settings.INSTALLED_APPS and hasattr(self.club, "weiclub") and self.club.weiclub)):
                # If the soge pays, then the transaction is unvalidated in a first time, then submitted for control
                # to treasurers.
                transaction.valid = False
                from treasury.models import SogeCredit
                soge_credit = SogeCredit.objects.get_or_create(user=self.user)[0]
                soge_credit.refresh_from_db()
                transaction.save(force_insert=True)
                transaction.refresh_from_db()
                soge_credit.transactions.add(transaction)
                soge_credit.save()
            else:
                transaction.save(force_insert=True)

    def __str__(self):
        return _("Membership of {user} for the club {club}").format(user=self.user.username, club=self.club.name, )

    class Meta:
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')
        indexes = [models.Index(fields=['user'])]
