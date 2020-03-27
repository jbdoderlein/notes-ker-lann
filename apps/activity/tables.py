# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from django_tables2 import tables, A

from .models import Activity, Guest


class ActivityTable(tables.Table):
    name = tables.columns.LinkColumn('activity:activity_detail',
                                     args=[A('pk'), ],)

    invite = tables.columns.LinkColumn('activity:activity_invite',
                                       args=[A('pk'), ],
                                       verbose_name=_("Invite"),
                                       text=_("Invite"),)

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Activity
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'activity_type', 'organizer', 'attendees_club', 'date_start', 'date_end', 'invite', )


class GuestTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Guest
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'inviter', )
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: record.pk
        }
