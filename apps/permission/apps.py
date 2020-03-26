# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.db.models.signals import pre_save, pre_delete


class PermissionConfig(AppConfig):
    name = 'permission'

    def ready(self):
        from . import signals
        pre_save.connect(signals.pre_save_object)
        pre_delete.connect(signals.pre_delete_object)
