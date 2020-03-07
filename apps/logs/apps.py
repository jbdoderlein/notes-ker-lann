# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LogsConfig(AppConfig):
    name = 'logs'
    verbose_name = _('Logs')

    def ready(self):
        # noinspection PyUnresolvedReferences
        import logs.signals
