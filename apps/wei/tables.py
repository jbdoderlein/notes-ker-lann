# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date

import django_tables2 as tables
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_tables2 import A
from note_kfet.middlewares import get_current_authenticated_user
from permission.backends import PermissionBackend

from .models import WEIClub, WEIRegistration, Bus, BusTeam, WEIMembership


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
        args=[A('user__pk')],
    )

    edit = tables.LinkColumn(
        'wei:wei_update_registration',
        orderable=False,
        args=[A('pk')],
        verbose_name=_("Edit"),
        text=_("Edit"),
        attrs={
            'a': {
                'class': 'btn btn-warning',
                'data-turbolinks': 'false',
            }
        }
    )

    validate = tables.Column(
        verbose_name=_("Validate"),
        orderable=False,
        accessor=A('pk'),
        attrs={
            'th': {
                'id': 'validate-membership-header'
            }
        }
    )

    delete = tables.LinkColumn(
        'wei:wei_delete_registration',
        args=[A('pk')],
        orderable=False,
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

    def render_validate(self, record):
        hasperm = PermissionBackend.check_perm(
            get_current_authenticated_user(), "wei.add_weimembership", WEIMembership(
                club=record.wei,
                user=record.user,
                date_start=date.today(),
                date_end=date.today(),
                fee=0,
                registration=record,
            )
        )
        if not hasperm:
            return format_html("<span class='no-perm'></span>")

        url = reverse_lazy('wei:validate_registration', args=(record.pk,))
        text = _('Validate')
        if record.fee > record.user.note.balance:
            btn_class = 'btn-secondary'
            tooltip = _("The user does not have enough money.")
        else:
            btn_class = 'btn-success'
            tooltip = _("The user has enough money, you can validate the registration.")

        return format_html(f"<a class=\"btn {btn_class}\" data-type='validate-membership' data-toggle=\"tooltip\" "
                           f"title=\"{tooltip}\" href=\"{url}\">{text}</a>")

    def render_delete(self, record):
        hasperm = PermissionBackend.check_perm(get_current_authenticated_user(), "wei.delete_weimembership", record)
        return _("Delete") if hasperm else format_html("<span class='no-perm'></span>")

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = WEIRegistration
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('user', 'user__first_name', 'user__last_name', 'first_year', 'caution_check',
                  'edit', 'validate', 'delete',)
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: record.pk
        }


class WEIMembershipTable(tables.Table):
    user = tables.LinkColumn(
        'wei:wei_update_registration',
        args=[A('registration__pk')],
    )

    year = tables.Column(
        accessor=A("pk"),
        verbose_name=_("Year"),
    )

    bus = tables.LinkColumn(
        'wei:manage_bus',
        args=[A('bus__pk')],
    )

    team = tables.LinkColumn(
        'wei:manage_bus_team',
        args=[A('team__pk')],
    )

    def render_year(self, record):
        return str(record.user.profile.ens_year) + "A"

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = WEIMembership
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('user', 'user__last_name', 'user__first_name', 'registration__gender', 'user__profile__department',
                  'year', 'bus', 'team', 'registration__caution_check', )
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
        }


class BusTable(tables.Table):
    name = tables.LinkColumn(
        'wei:manage_bus',
        args=[A('pk')],
    )

    teams = tables.Column(
        accessor=A("teams"),
        verbose_name=_("Teams"),
        attrs={
            "td": {
                "class": "text-truncate",
            }
        }
    )

    count = tables.Column(
        verbose_name=_("Members count"),
    )

    def render_teams(self, value):
        return ", ".join(team.name for team in value.order_by('name').all())

    def render_count(self, value):
        return str(value) + " " + (str(_("members")) if value > 1 else str(_("member")))

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Bus
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'teams', )
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
        }


class BusTeamTable(tables.Table):
    name = tables.LinkColumn(
        'wei:manage_bus_team',
        args=[A('pk')],
    )

    color = tables.Column(
        attrs={
            "td": {
                "style": lambda record: "background-color: #{:06X}; color: #{:06X};"
                                        .format(record.color, 0xFFFFFF - record.color, )
            }
        }
    )

    def render_count(self, value):
        return str(value) + " " + (str(_("members")) if value > 1 else str(_("member")))

    count = tables.Column(
        verbose_name=_("Members count"),
    )

    def render_color(self, value):
        return "#{:06X}".format(value)

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = BusTeam
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'color',)
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: reverse_lazy('wei:manage_bus_team', args=(record.pk, ))
        }
