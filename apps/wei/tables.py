# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_tables2 import A

from .models import WEIClub, WEIRegistration


class WEITable(tables.Table):
    """
    List all WEI.
    """
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = WEIClub
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'year', 'date_start', 'date_end',)
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: reverse_lazy('wei:wei_detail', args=(record.pk,))
        }


class WEIRegistrationTable(tables.Table):
    """
    List all WEI registrations.
    """
    user = tables.LinkColumn(
        'member:user_detail',
        args=[A('user.pk')],
    )

    edit = tables.LinkColumn(
        'wei:wei_detail',
        args=[A('pk')],
        verbose_name=_("Edit"),
        text=_("Edit"),
        attrs={
            'a': {
                'class': 'btn btn-warning'
            }
        }
    )
    validate = tables.LinkColumn(
        'wei:wei_detail',
        args=[A('pk')],
        verbose_name=_("Validate"),
        text=_("Validate"),
        attrs={
            'a': {
                'class': 'btn btn-success'
            }
        }
    )

    delete = tables.LinkColumn(
        'wei:wei_detail',
        args=[A('pk')],
        verbose_name=_("delete"),
        text=_("Delete"),
        attrs={
            'a': {
                'class': 'btn btn-danger'
            }
        },
    )

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = WEIRegistration
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('user',)
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: record.pk
        }
