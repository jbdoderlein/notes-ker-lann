# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import html

import django_tables2 as tables
from django.db.models import F
from django_tables2.utils import A

from .models.notes import Alias
from .models.transactions import Transaction
from .templatetags.pretty_money import pretty_money


class HistoryTable(tables.Table):
    class Meta:
        attrs = {
            'class':
                'table table-condensed table-striped table-hover'
        }
        model = Transaction
        exclude = ("id", "polymorphic_ctype", )
        template_name = 'django_tables2/bootstrap4.html'
        sequence = ('...', 'total', 'valid', )
        orderable = False

    total = tables.Column()  # will use Transaction.total() !!

    valid = tables.Column(attrs={"td": {"id": lambda record: "validate_" + str(record.id),
                                        "class": lambda record: str(record.valid).lower() + ' validate'}})

    def order_total(self, queryset, is_descending):
        # needed for rendering
        queryset = queryset.annotate(total=F('amount') * F('quantity')) \
            .order_by(('-' if is_descending else '') + 'total')
        return queryset, True


    def render_amount(self, value):
        return pretty_money(value)


    def render_total(self, value):
        return pretty_money(value)


    # Django-tables escape strings. That's a wrong thing.
    def render_reason(self, value):
        return html.unescape(value)


    def render_valid(self, value):
        return "✔" if value else "✖"


class AliasTable(tables.Table):
    class Meta:
        attrs = {
            'class':
                'table table condensed table-striped table-hover'
        }
        model = Alias
        fields = ('name',)
        template_name = 'django_tables2/bootstrap4.html'

    show_header = False
    name = tables.Column(attrs={'td': {'class': 'text-center'}})
    delete = tables.LinkColumn('member:user_alias_delete',
                               args=[A('pk')],
                               attrs={
                                   'td': {'class': 'col-sm-2'},
                                   'a': {'class': 'btn btn-danger'}},
                               text='delete', accessor='pk')
