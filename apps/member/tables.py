# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.contrib.auth.models import User

from .models import Club


class ClubTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Club
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id', 'name', 'email')
        row_attrs = {
            'class': 'table-row',
            'data-href': lambda record: record.pk
        }


class UserTable(tables.Table):
    section = tables.Column(accessor='profile.section')
    solde = tables.Column(accessor='note.balance')

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('last_name', 'first_name', 'username', 'email')
        model = User
