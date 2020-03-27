# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from django_tables2 import A

from .models import Activity, Guest


class ActivityTable(tables.Table):
    name = tables.LinkColumn(
        'activity:activity_detail',
        args=[A('pk'), ],
    )

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Activity
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'activity_type', 'organizer', 'attendees_club', 'date_start', 'date_end', )


class GuestTable(tables.Table):
    inviter = tables.LinkColumn(
        'member:user_detail',
        args=[A('inviter.user.pk'), ],
    )

    entry = tables.Column(
        empty_values=(),
        attrs={
            "td": {
                "class": lambda record: "" if record.entry else "validate btn btn-danger",
                "onclick": lambda record: "" if record.entry else "remove_guest(" + str(record.pk) + ")"
            }
        }
    )

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Guest
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("last_name", "first_name", "inviter", )

    def render_entry(self, record):
        if record.entry:
            return str(record.date)
        return _("remove").capitalize()
