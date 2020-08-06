# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django import template


def do_latex_escape(value):
    return (
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
