# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2 import A

from .models import Invoice


class InvoiceTable(tables.Table):
    id = tables.LinkColumn("treasury:invoice_update",
                           args=[A("pk")],
                           text=lambda record: _("Invoice #{:d}").format(record.id), )

    invoice = tables.LinkColumn("treasury:invoice_render",
                                verbose_name=_("Invoice"),
                                args=[A("pk")],
                                accessor="pk",
                                text="",
                                attrs={
                                    'a': {'class': 'fa fa-file-pdf-o'},
                                    'td': {'data-turbolinks': 'false'}
                                })

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Invoice
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id', 'name', 'object', 'acquitted', 'invoice',)
