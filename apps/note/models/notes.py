# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import unicodedata

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

"""
Defines each note types
"""


class Note(PolymorphicModel):
    """
    Gives transactions capabilities. Note is a Polymorphic Model, use as based
    for the models :model:`note.NoteUser` and :model:`note.NoteClub`.
    A Note principaly store the actual balance of someone/some club.
    A Note can be searched find throught an :model:`note.Alias`

    """
    balance = models.IntegerField(
        verbose_name=_('account balance'),
        help_text=_('in centimes, money credited for this instance'),
        default=0,
    )
    last_negative = models.DateTimeField(
        verbose_name=_('last negative date'),
        help_text=_('last time the balance was negative'),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this note should be treated as active. '
            'Unselect this instead of deleting notes.'),
    )
    display_image = models.ImageField(
        verbose_name=_('display image'),
        max_length=255,
        blank=False,
        null=False,
        upload_to='pic/',
        default='pic/default.png'
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")

    def pretty(self):
        """
        :return: Pretty name of this note
        """
        return str(self)

    pretty.short_description = _('Note')

    def save(self, *args, **kwargs):
        """
        Save note with it's alias (called in polymorphic children)
        """
        aliases = Alias.objects.filter(name=str(self))
        if aliases.exists():
            # Alias exists, so check if it is linked to this note
            if aliases.first().note != self:
                raise ValidationError(_('This alias is already taken.'),
                                      code="same_alias")

            # Save note
            super().save(*args, **kwargs)
        else:
            # Alias does not exist yet, so check if it can exist
            a = Alias(name=str(self))
            a.clean()

            # Save note and alias
            super().save(*args, **kwargs)
            a.note = self
            a.save(force_insert=True)

    def clean(self, *args, **kwargs):
        """
        Verify alias (simulate save)
        """
        aliases = Alias.objects.filter(
            normalized_name=Alias.normalize(str(self)))
        if aliases.exists():
            # Alias exists, so check if it is linked to this note
            if aliases.first().note != self:
                raise ValidationError(_('This alias is already taken.'),
                                      code="same_alias", )
        else:
            # Alias does not exist yet, so check if it can exist
            a = Alias(name=str(self))
            a.clean()


class NoteUser(Note):
    """
    A :model:`note.Note` associated to an  unique :model:`auth.User`.
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
        return str(self.user)

    def pretty(self):
        return _("%(user)s's note") % {'user': str(self.user)}


class NoteClub(Note):
    """
    A :model:`note.Note` associated to an unique :model:`member.Club`
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
        return str(self.club)

    def pretty(self):
        return _("Note of %(club)s club") % {'club': str(self.club)}


class NoteSpecial(Note):
    """
    A :model:`note.Note` for special accounts, where real money enter or leave the system
    - bank check
    - credit card
    - bank transfer
    - cash
    - refund
    This Type of Note is not associated to a :model:`auth.User` or :model:`member.Club` .
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


class Alias(models.Model):
    """
    points toward  a :model:`note.NoteUser` or :model;`note.NoteClub` instance.
    Alias are unique, but a :model:`note.NoteUser` or :model:`note.NoteClub` can
    have multiples aliases.

    Aliases name are also normalized, two differents :model:`note.Note` can not
    have the same normalized alias, to avoid confusion when referring orally to
    it.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                regex=settings.ALIAS_VALIDATOR_REGEX,
                message=_('Invalid alias'),
            )
        ] if settings.ALIAS_VALIDATOR_REGEX else [],
    )
    normalized_name = models.CharField(
        max_length=255,
        unique=True,
        default='',
        editable=False,
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _("alias")
        verbose_name_plural = _("aliases")
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['normalized_name']),
        ]

    def __str__(self):
        return self.name

    @staticmethod
    def normalize(string):
        """
        Normalizes a string: removes most diacritics and does casefolding
        """
        return ''.join(
            char for char in unicodedata.normalize('NFKD', string.casefold())
            if all(not unicodedata.category(char).startswith(cat)
                   for cat in {'M', 'P', 'Z', 'C'})).casefold()

    def clean(self):
        normalized_name = self.normalize(self.name)
        if len(normalized_name) >= 255:
            raise ValidationError(_('Alias is too long.'),
                                  code='alias_too_long')
        try:
            sim_alias = Alias.objects.get(normalized_name=normalized_name)
            if self != sim_alias:
                raise ValidationError(_('An alias with a similar name already exists: {} ').format(sim_alias),
                                      code="same_alias"
                                      )
        except Alias.DoesNotExist:
            pass
        self.normalized_name = normalized_name

    def save(self,*args,**kwargs):
        self.normalized_name = self.normalize(self.name)
        super().save(*args,**kwargs)
        
    def delete(self, using=None, keep_parents=False):
        if self.name == str(self.note):
            raise ValidationError(_("You can't delete your main alias."),
                                  code="main_alias")
        return super().delete(using, keep_parents)
