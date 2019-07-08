# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Alias(models.Model):
    """
    A alias labels a Note instance, only for user and clubs
    """
    alias = models.TextField(
        "alias",
        unique = True,
        blank = False,
        null = False,
    )
    limit = models.Q(app_label="note", model="NoteUser") | models.Q(app_label="note",model="NoteClub")

    owner_id = models.PositiveIntegerField()
    owner_type = models.ForeignKey(ContentType,
                                   on_delete=models.CASCADE,
                                   limit_choices_to=limit)
    owner = GenericForeignKey('owner_type','owner_id')

class Note(models.Model):
    """
    An abstract model, use to add transactions capabilities to a user
    """

    solde = models.IntegerField(
        verbose_name=_('solde du compte'),
        help_text=_("en centime, l' argent crédité pour cette instance")
    )
    active = models.BooleanField(
        default = True,
        verbose_name=_('etat du compte')
    )

    class Meta:
        abstract = True

class NoteUser(Note):
    """
    A Note associated to a User
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    class Meta:
        verbose_name = _("One's Note")
        verbose_name_plural = _("Users Note")

    def __str__(self):
        return self.user.get_username()

    aliases = models.ForeignKey(Aliases)



class NoteSpec(Note):
    """
    A Note for special Account, where real money enter or leave the system.
     - Cash
     - Credit Card
     - Bank Transfert
     - Bank Check
     - Refund
    """
    account_type = models.CharField(
        max_length = 2,
        choices = (("CH","chèques"),
                   ("CB","Carte Bancaire"),
                   ("VB","Virement Bancaire"),
                   ("CA","Cash"),
                   ("RB","Remboursement")
        ),
        unique = True
    )

class NoteClub(Note):
    #to be added
    pass
