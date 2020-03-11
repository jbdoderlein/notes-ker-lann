# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save, post_delete
from django.utils.translation import gettext_lazy as _


class LogsConfig(AppConfig):
    name = 'logs'
    verbose_name = _('Logs')

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals
        pre_save.connect(signals.pre_save_object)
        post_save.connect(signals.save_object)
        post_delete.connect(signals.delete_object)
