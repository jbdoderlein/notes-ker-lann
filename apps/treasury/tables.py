# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_tables2 import tables

from .models import Billing


class BillingTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Billing
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id', 'name', 'subject', 'acquitted', )
        row_attrs = {
            'class': 'table-row',
            'data-href': lambda record: record.pk
        }