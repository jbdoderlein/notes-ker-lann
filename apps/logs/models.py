# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Changelog(models.Model):
    """
    Store each modification in the database (except sessions and logging),
    including creating, editing and deleting models.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_('user'),
    )

    ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP Address")
    )

    model = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('model'),
    )

    instance_pk = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name=_('identifier'),
    )

    previous = models.TextField(
        null=True,
        verbose_name=_('previous data'),
    )

    data = models.TextField(
        null=True,
        verbose_name=_('new data'),
    )

    action = models.CharField(  # create, edit or delete
        max_length=16,
        null=False,
        blank=False,
        verbose_name=_('action'),
    )

    timestamp = models.DateTimeField(
        null=False,
        blank=False,
        auto_now_add=True,
        name='timestamp',
        verbose_name=_('timestamp'),
    )

    def delete(self, using=None, keep_parents=False):
        raise ValidationError(_("Logs cannot be destroyed."))
