# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.urls import reverse_lazy

from wei.models import WEIClub


class WEITable(tables.Table):
    """
    List all clubs.
    """
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = WEIClub
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'year', 'date_start', 'date_end',)
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: reverse_lazy('member:club_detail', args=(record.pk,))
        }
