# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import template

import os


def getenv(value):
    return os.getenv(value)


register = template.Library()
register.filter('getenv', getenv)
