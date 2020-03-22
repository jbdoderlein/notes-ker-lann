# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import template


def pretty_money(value):
    if value % 100 == 0:
        return "{:s}{:d} €".format(
            "- " if value < 0 else "",
            abs(value) // 100,
        )
    else:
        return "{:s}{:d}.{:02d} €".format(
            "- " if value < 0 else "",
            abs(value) // 100,
            abs(value) % 100,
        )


def cents_to_euros(value):
    return "{:.02f}".format(value / 100) if value else ""


register = template.Library()
register.filter('pretty_money', pretty_money)
register.filter('cents_to_euros', cents_to_euros)
