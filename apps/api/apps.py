# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class APIConfig(AppConfig):
    name = 'api'
    verbose_name = _('API')
