# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.contrib.auth.models import User


class FutureUserTable(tables.Table):
    """
    Display the list of pre-registered users
    """
    phone_number = tables.Column(accessor='profile.phone_number')

    section = tables.Column(accessor='profile.section')

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('last_name', 'first_name', 'username', 'email', )
        model = User
        row_attrs = {
            'class': 'table-row',
            'data-href': lambda record: record.pk
        }
