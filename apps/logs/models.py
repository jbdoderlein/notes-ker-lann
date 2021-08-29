# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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
        blank=True,
        default="",
        verbose_name=_('previous data'),
    )

    data = models.TextField(
        blank=True,
        default="",
        verbose_name=_('new data'),
    )

    action = models.CharField(  # create, edit or delete
        max_length=16,
        null=False,
        blank=False,
        choices=[
            ('create', _('create')),
            ('edit', _('edit')),
            ('delete', _('delete')),
        ],
        default='edit',
        verbose_name=_('action'),
    )

    timestamp = models.DateTimeField(
        null=False,
        blank=False,
        default=timezone.now,
        name='timestamp',
        verbose_name=_('timestamp'),
    )

    def delete(self, using=None, keep_parents=False):
        raise ValidationError(_("Logs cannot be destroyed."))

    class Meta:
        verbose_name = _("changelog")
        verbose_name_plural = _("changelogs")

    def __str__(self):
        return _("Changelog of type \"{action}\" for model {model} at {timestamp}").format(
            action=self.get_action_display(), model=str(self.model), timestamp=str(self.timestamp))
