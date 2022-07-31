# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2 import A
from note.models import SpecialTransaction
from note.templatetags.pretty_money import pretty_money

from .models import Invoice, Remittance


class InvoiceTable(tables.Table):
    """
    List all invoices.
    """
    id = tables.LinkColumn(
        "treasury:invoice_update",
        args=[A("pk")],
        text=lambda record: _("Invoice #{:d}").format(record.id),
    )

    invoice = tables.LinkColumn(
        "treasury:invoice_render",
        verbose_name=_("Invoice"),
        args=[A("pk")],
        accessor="pk",
        text="",
        attrs={
            'a': {'class': 'fa fa-file-pdf-o'},
            'td': {'data-turbolinks': 'false'}
        }
    )

    delete = tables.LinkColumn(
        'treasury:invoice_delete',
        args=[A('id')],
        verbose_name=_("delete"),
        text=_("Delete"),
        attrs={
            'th': {
                'id': 'delete-membership-header'
            },
            'a': {
                'class': 'btn btn-danger',
                'data-type': 'delete-membership'
            }
        },
    )

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Invoice
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id', 'name', 'object', 'acquitted', 'invoice',)


class RemittanceTable(tables.Table):
    """
    List all remittances.
    """

    count = tables.Column(verbose_name=_("Transaction count"))

    amount = tables.Column(verbose_name=_("Amount"))

    view = tables.LinkColumn("treasury:remittance_update",
                             verbose_name=_("View"),
                             args=[A("pk")],
                             text=_("View"),
                             attrs={
                                 'a': {'class': 'btn btn-primary'}
                             }, )

    def render_amount(self, value):
        return pretty_money(value)

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Remittance
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id', 'date', 'remittance_type', 'comment', 'count', 'amount', 'view',)
        order_by = ('-date',)


class SpecialTransactionTable(tables.Table):
    """
    List special credit transactions that are (or not, following the queryset) attached to a remittance.
    """

    # Display add and remove buttons. Use the `exclude` field to select what is needed.
    remittance_add = tables.LinkColumn("treasury:link_transaction",
                                       verbose_name=_("Remittance"),
                                       args=[A("specialtransactionproxy__pk")],
                                       text=_("Add"),
                                       attrs={
                                           'a': {'class': 'btn btn-primary'}
                                       }, )

    remittance_remove = tables.LinkColumn("treasury:unlink_transaction",
                                          verbose_name=_("Remittance"),
                                          args=[A("specialtransactionproxy__pk")],
                                          text=_("Remove"),
                                          attrs={
                                              'a': {'class': 'btn btn-primary btn-danger'}
                                          }, )

    def render_amount(self, value):
        return pretty_money(value)

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = SpecialTransaction
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('created_at', 'source', 'destination', 'last_name', 'first_name', 'bank', 'amount', 'reason',)
        order_by = ('-created_at',)
