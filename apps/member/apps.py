# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from .signals import save_user_profile


class MemberConfig(AppConfig):
    name = 'member'
    verbose_name = _('member')

    def ready(self):
        """
        Define app internal signals to interact with other apps
        """
        post_save.connect(
            save_user_profile,
            sender=settings.AUTH_USER_MODEL,
        )
