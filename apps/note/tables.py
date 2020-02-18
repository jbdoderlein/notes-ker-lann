# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.db.models import F

from .models.transactions import Transaction


class HistoryTable(tables.Table):
    class Meta:
        attrs = {
            'class':
            'table table-bordered table-condensed table-striped table-hover'
        }
        model = Transaction
        template_name = 'django_tables2/bootstrap.html'
        sequence = ('...', 'total', 'valid')

    total = tables.Column()  # will use Transaction.total() !!

    def order_total(self, queryset, is_descending):
        # needed for rendering
        queryset = queryset.annotate(total=F('amount') * F('quantity')) \
            .order_by(('-' if is_descending else '') + 'total')
        return (queryset, True)
