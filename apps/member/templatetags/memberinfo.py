# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date

from django import template
from django.contrib.auth.models import User

from ..models import Club, Membership


def is_member(user, club):
    if isinstance(user, str):
        club = User.objects.get(username=user)
    if isinstance(club, str):
        club = Club.objects.get(name=club)
    return Membership.objects\
        .filter(user=user, club=club, date_start__lte=date.today(), date_end__gte=date.today()).exists()


register = template.Library()
register.filter("is_member", is_member)
