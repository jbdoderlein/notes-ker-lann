# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save, post_delete
from django.utils.translation import gettext_lazy as _


class TreasuryConfig(AppConfig):
    name = 'treasury'
    verbose_name = _('Treasury')
