# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import template
from django.utils.safestring import mark_safe


def do_latex_escape(value):
    return mark_safe(
        value.replace("&", "\\&")
        .replace("$", "\\$")
        .replace("%", "\\%")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("\n", "\\\\")
        .replace("\r", "")
    )


register = template.Library()
register.filter("escape_tex", do_latex_escape)
