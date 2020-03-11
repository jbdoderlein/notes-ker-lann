# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import template

from .getenv import getenv
from .pretty_money import pretty_money

register = template.Library()

register.filter('getenv', getenv)
register.filter('pretty_money', pretty_money)
