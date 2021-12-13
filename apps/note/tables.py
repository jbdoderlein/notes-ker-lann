# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import html

import django_tables2 as tables
from django.utils.html import format_html, mark_safe
from django_tables2.utils import A
from django.utils.translation import gettext_lazy as _
from note_kfet.middlewares import get_current_request
from permission.backends import PermissionBackend

from .models.notes import Alias
from .models.transactions import Transaction, TransactionTemplate
from .templatetags.pretty_money import pretty_money


class HistoryTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped'
        }
        model = Transaction
        exclude = ("id", "polymorphic_ctype", "invalidity_reason", "source_alias", "destination_alias",)
        template_name = 'django_tables2/bootstrap4.html'
        sequence = ('...', 'type', 'total', 'valid',)
        orderable = False

    source = tables.Column(
        attrs={
            "td": {
                "class": "text-nowrap",
                "data-toggle": "tooltip",
                "title": lambda record: _("used alias").capitalize() + " : " + record.source_alias,
            }
        }
    )

    destination = tables.Column(
        attrs={
            "td": {
                "class": "text-nowrap",
                "data-toggle": "tooltip",
                "title": lambda record: _("used alias").capitalize() + " : " + record.destination_alias,
            }
        }
    )

    created_at = tables.DateTimeColumn(
        format='Y-m-d H:i:s',
        attrs={
            "td": {
                "class": "text-nowrap",
            },
        }
    )

    amount = tables.Column(
        attrs={
            "td": {
                "class": "text-nowrap",
            },
        }
    )

    reason = tables.Column(
        attrs={
            "td": {
                "class": "text-break",
            },
        }
    )

    type = tables.Column()

    total = tables.Column(  # will use Transaction.total() !!
        attrs={
            "td": {
                "class": "text-nowrap",
            },
        }
    )

    valid = tables.Column(
        attrs={
            "td": {
                "id": lambda record: "validate_" + str(record.id),
                "class": lambda record:
                str(record.valid).lower()
                + (' validate' if record.source.is_active and record.destination.is_active and PermissionBackend
                   .check_perm(get_current_request(), "note.change_transaction_invalidity_reason", record)
                   else ''),
                "data-toggle": "tooltip",
                "title": lambda record: (_("Click to invalidate") if record.valid else _("Click to validate"))
                if PermissionBackend.check_perm(get_current_request(),
                                                "note.change_transaction_invalidity_reason", record)
                and record.source.is_active and record.destination.is_active else None,
                "onclick": lambda record: 'de_validate(' + str(record.id) + ', ' + str(record.valid).lower()
                                          + ', "' + str(record.__class__.__name__) + '")'
                if PermissionBackend.check_perm(get_current_request(),
                                                "note.change_transaction_invalidity_reason", record)
                and record.source.is_active and record.destination.is_active else None,
                "onmouseover": lambda record: '$("#invalidity_reason_'
                                              + str(record.id) + '").show();$("#invalidity_reason_'
                                              + str(record.id) + '").focus();',
                "onmouseout": lambda record: '$("#invalidity_reason_' + str(record.id) + '").hide()',
            }
        }
    )

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
        has_perm = PermissionBackend \
            .check_perm(get_current_request(), "note.change_transaction_invalidity_reason", record)

        val = "✔" if value else "✖"

        if value and not has_perm:
            return val

        val += "<input type='text' class='form-control' id='invalidity_reason_" + str(record.id) \
               + "' value='" + (html.escape(record.invalidity_reason)
                                if record.invalidity_reason else ("" if value else str(_("No reason specified")))) \
               + "'" + ("" if value and record.source.is_active and record.destination.is_active else " disabled") \
               + " placeholder='" + html.escape(_("invalidity reason").capitalize()) + "'" \
               + " style='position: absolute; width: 15em; margin-left: -15.5em; margin-top: -2em; display: none;'>"
        return format_html(val)


# function delete_button(id) provided in template file
DELETE_TEMPLATE = """
    <button id="{{ record.pk }}" class="btn btn-danger btn-sm" onclick="delete_button(this.id)"> {{ delete_trans }}</button>
"""


class AliasTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'table table condensed table-striped',
            'id': "alias_table"
        }
        model = Alias
        fields = ('name',)
        template_name = 'django_tables2/bootstrap4.html'

    show_header = False
    name = tables.Column(attrs={'td': {'class': 'text-center'}})

    delete_col = tables.TemplateColumn(template_code=DELETE_TEMPLATE,
                                       extra_context={"delete_trans": _('delete')},
                                       attrs={'td': {'class': lambda record: 'col-sm-1' + (
                                           ' d-none' if not PermissionBackend.check_perm(
                                               get_current_request(), "note.delete_alias",
                                               record) else '')}}, verbose_name=_("Delete"), )


class ButtonTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'table table-bordered condensed'
        }
        row_attrs = {
            'class': lambda record: 'table-row ' + ('table-success' if record.display else 'table-danger'),
            'id': lambda record: "row-" + str(record.pk),
        }

        model = TransactionTemplate
        exclude = ('id',)

    edit = tables.LinkColumn(
        'note:template_update',
        args=[A('pk')],
        attrs={
            'td': {'class': 'col-sm-1'},
            'a': {
                'class': 'btn btn-sm btn-primary',
                'data-turbolinks': 'false',
            }
        },
        text=_('edit'),
        accessor='pk',
        verbose_name=_("Edit"),
    )

    hideshow = tables.Column(
            verbose_name= _("Hide/Show"),
            accessor="pk",
            attrs= {
                'td': {
                    'class': 'col-sm-1',
                    'id': lambda record: "hideshow_" + str(record.pk),
                    }
                })

    delete_col = tables.TemplateColumn(template_code=DELETE_TEMPLATE,
                                       extra_context={"delete_trans": _('delete')},
                                       attrs={'td': {'class': 'col-sm-1'}},
                                       verbose_name=_("Delete"), )

    def render_amount(self, value):
        return pretty_money(value)

    def order_category(self, queryset, is_descending):
        return queryset.order_by(f"{'-' if is_descending else ''}category__name"), True

    def render_hideshow(self, record):
        val = '<button id="'
        val += str(record.pk)
        val += '" class="btn btn-secondary btn-sm" \
            onclick="hideshow(' + str(record.id) + ',' + \
            str(record.display).lower() + ')">'
        val += str(_("Hide/Show"))
        val += '</button>'
        return mark_safe(val)
