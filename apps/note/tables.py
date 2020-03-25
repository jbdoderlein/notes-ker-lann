# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import html

import django_tables2 as tables
from django.db.models import F
from django.utils.html import format_html
from django_tables2.utils import A
from django.utils.translation import gettext_lazy as _

from .models.notes import Alias
from .models.transactions import Transaction, TransactionTemplate
from .templatetags.pretty_money import pretty_money


class HistoryTable(tables.Table):
    class Meta:
        attrs = {
            'class':
                'table table-condensed table-striped table-hover'
        }
        model = Transaction
        exclude = ("id", "polymorphic_ctype", "invalidity_reason")
        template_name = 'django_tables2/bootstrap4.html'
        sequence = ('...', 'type', 'total', 'valid',)
        orderable = False

    type = tables.Column()

    total = tables.Column()  # will use Transaction.total() !!

    valid = tables.Column(
        attrs={
            "td": {
                "id": lambda record: "validate_" + str(record.id),
                "class": lambda record: str(record.valid).lower() + ' validate',
                "data-toggle": "tooltip",
                "title": lambda record: _("Click to invalidate") if record.valid else _("Click to validate"),
                "onclick": lambda record: 'in_validate(' + str(record.id) + ', ' + str(record.valid).lower() + ')',
                "onmouseover": lambda record: '$("#invalidity_reason_'
                                              + str(record.id) + '").show();$("#invalidity_reason_'
                                              + str(record.id) + '").focus();',
                "onmouseout": lambda record: '$("#invalidity_reason_' + str(record.id) + '").hide()',
            }
        }
    )

    def order_total(self, queryset, is_descending):
        # needed for rendering
        queryset = queryset.annotate(total=F('amount') * F('quantity')) \
            .order_by(('-' if is_descending else '') + 'total')
        return queryset, True

    def render_amount(self, value):
        return pretty_money(value)

    def render_total(self, value):
        return pretty_money(value)

    def render_type(self, value):
        return _(value)

    # Django-tables escape strings. That's a wrong thing.
    def render_reason(self, value):
        return html.unescape(value)

    def render_valid(self, value, record):
        """
        When the validation status is hovered, an input field is displayed to let the user specify an invalidity reason
        """
        val = "✔" if value else "✖"
        val += "<input type='text' class='form-control' id='invalidity_reason_" + str(record.id) \
               + "' value='" + (html.escape(record.invalidity_reason)
                                if record.invalidity_reason else ("" if value else str(_("No reason specified")))) \
               + "'" + ("" if value else " disabled") \
               + " placeholder='" + html.escape(_("invalidity reason").capitalize()) + "'" \
               + " style='position: absolute; width: 15em; margin-left: -15.5em; margin-top: -2em; display: none;'>"
        return format_html(val)


# function delete_button(id) provided in template file
DELETE_TEMPLATE = """
    <button id="{{ record.pk }}" class="btn btn-danger" onclick="delete_button(this.id)"> {{ delete_trans }}</button>
"""


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
    # delete = tables.TemplateColumn(template_code=delete_template,
    #                                attrs={'td':{'class': 'col-sm-1'}})

    delete = tables.LinkColumn('member:user_alias_delete',
                               args=[A('pk')],
                               attrs={
                                   'td': {'class': 'col-sm-2'},
                                   'a': {'class': 'btn btn-danger'}},
                               text='delete', accessor='pk')


class ButtonTable(tables.Table):
    class Meta:
        attrs = {
            'class':
                'table table-bordered condensed table-hover'
        }
        row_attrs = {
            'class': lambda record: 'table-row ' + 'table-success' if record.display else 'table-danger',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: record.pk
        }

        model = TransactionTemplate

    edit = tables.LinkColumn('note:template_update',
                             args=[A('pk')],
                             attrs={'td': {'class': 'col-sm-1'},
                                    'a': {'class': 'btn btn-primary'}},
                             text=_('edit'),
                             accessor='pk')

    delete = tables.TemplateColumn(template_code=DELETE_TEMPLATE,
                                   extra_context={"delete_trans": _('delete')},
                                   attrs={'td': {'class': 'col-sm-1'}})

    def render_amount(self, value):
        return pretty_money(value)
