# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.db.models import F

from .models.transactions import Transaction
from .models.notes import Alias

class HistoryTable(tables.Table):
    class Meta:
        attrs = {
            'class':
            'table table-condensed table-striped table-hover'
        }
        model = Transaction
        template_name = 'django_tables2/bootstrap4.html'
        sequence = ('...', 'total', 'valid')

    total = tables.Column()  # will use Transaction.total() !!

    def order_total(self, queryset, is_descending):
        # needed for rendering
        queryset = queryset.annotate(total=F('amount') * F('quantity')) \
            .order_by(('-' if is_descending else '') + 'total')
        return (queryset, True)

class AliasTable(tables.Table):
    class Meta:
        attrs = {
            'class':
            'table table condensed table-striped table-hover'
        }
        model = Alias
        fields = ('name',)
        template_name = 'django_tables2/bootstrap4.html'

    delete = tables.LinkColumn('member:user_alias_delete', args=[A('id')], attrs={
        'a': {'class': 'btn'} })
