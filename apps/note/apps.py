# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from . import signals


class NoteConfig(AppConfig):
    name = 'note'
    verbose_name = _('note')

    def ready(self):
        """
        Define app internal signals to interact with other apps
        """
        post_save.connect(
            signals.save_user_note,
            sender=settings.AUTH_USER_MODEL,
        )
        post_save.connect(
            signals.save_club_note,
            sender='member.Club',
        )
