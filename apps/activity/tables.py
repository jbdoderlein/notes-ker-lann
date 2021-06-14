# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from django_tables2 import A
from note.templatetags.pretty_money import pretty_money

from .models import Activity, Entry, Guest


class ActivityTable(tables.Table):
    name = tables.LinkColumn(
        'activity:activity_detail',
        args=[A('pk'), ],
    )

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        row_attrs = {
            'class': lambda record: 'bg-success' if record.open else ('' if record.valid else 'bg-warning'),
            'title': lambda record: _("The activity is currently open.") if record.open else
            ('' if record.valid else _("The validation of the activity is pending.")),
        }
        model = Activity
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'activity_type', 'organizer', 'attendees_club', 'date_start', 'date_end', )


class GuestTable(tables.Table):
    inviter = tables.LinkColumn(
        'member:user_detail',
        args=[A('inviter__user__pk'), ],
    )

    entry = tables.Column(
        empty_values=(),
        verbose_name=_("Remove"),
    )

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped'
        }
        model = Guest
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("last_name", "first_name", "inviter", )

    def render_entry(self, record):
        if record.has_entry:
            return str(_("Entered on ") + str(_("{:%Y-%m-%d %H:%M:%S}").format(record.entry.time, )))
        return format_html('<button id="{id}" class="btn btn-danger btn-sm" onclick="remove_guest(this.id)"> '
                           '{delete_trans}</button>'.format(id=record.id, delete_trans=_("remove").capitalize()))


def get_row_class(record):
    c = "table-row"
    if isinstance(record, Guest):
        if record.has_entry:
            c += " table-success"
        else:
            c += " table-warning"
    else:
        qs = Entry.objects.filter(note=record.note, activity=record.activity, guest=None)
        if qs.exists():
            c += " table-success"
        elif not record.note.user.memberships.filter(club=record.activity.attendees_club,
                                                     date_start__lte=timezone.now(),
                                                     date_end__gte=timezone.now()).exists():
            c += " table-info"
        elif record.note.balance < 0:
            c += " table-danger"
    return c


class EntryTable(tables.Table):
    type = tables.Column(verbose_name=_("Type"))

    last_name = tables.Column(verbose_name=_("Last name"))

    first_name = tables.Column(verbose_name=_("First name"))

    note_name = tables.Column(verbose_name=_("Note"))

    balance = tables.Column(verbose_name=_("Balance"))

    def render_note_name(self, value, record):
        if hasattr(record, 'username'):
            username = record.username
            if username != value:
                return format_html(value + " <em>aka.</em> " + username)
        return value

    def render_balance(self, value):
        return pretty_money(value)

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        template_name = 'django_tables2/bootstrap4.html'
        row_attrs = {
            'class': lambda record: get_row_class(record),
            'id': lambda record: "row-" + ("guest-" if isinstance(record, Guest) else "membership-") + str(record.pk),
            'data-type': lambda record: "guest" if isinstance(record, Guest) else "membership",
            'data-id': lambda record: record.pk if isinstance(record, Guest) else record.note.pk,
            'data-inviter': lambda record: record.inviter.pk if isinstance(record, Guest) else "",
            'data-last-name': lambda record: record.last_name,
            'data-first-name': lambda record: record.first_name,
        }
