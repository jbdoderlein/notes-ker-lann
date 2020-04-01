# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from datetime import datetime

import django_tables2 as tables
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.utils.html import format_html
from note.templatetags.pretty_money import pretty_money
from note_kfet.middlewares import get_current_authenticated_user
from permission.backends import PermissionBackend

from .models import Club, Membership


class ClubTable(tables.Table):
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        model = Club
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id', 'name', 'email')
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: record.pk
        }


class UserTable(tables.Table):
    section = tables.Column(accessor='profile.section')
    solde = tables.Column(accessor='note.balance')

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('last_name', 'first_name', 'username', 'email')
        model = User


class MembershipTable(tables.Table):
    roles = tables.Column(
        attrs={
            "td": {
                "class": "text-truncate",
            }
        }
    )

    def render_club(self, value):
        s = value.name
        if PermissionBackend().has_perm(get_current_authenticated_user(), "member.view_club", value):
            s = format_html("<a href={url}>{name}</a>",
                            url=reverse_lazy('member:club_detail', kwargs={"pk": value.pk}), name=s)

        return s

    def render_fee(self, value, record):
        t = pretty_money(value)

        # If it is required and if the user has the right, the renew button is displayed.
        if record.club.membership_start is not None:
            if record.date_start < record.club.membership_start:  # If the renew is available
                if not Membership.objects.filter(
                        club=record.club,
                        user=record.user,
                        date_start__gte=record.club.membership_start,
                        date_end__lte=record.club.membership_end,
                ).exists():  # If the renew is not yet performed
                    empty_membership = Membership(
                        club=record.club,
                        user=record.user,
                        date_start=datetime.now().date(),
                        date_end=datetime.now().date(),
                        fee=0,
                    )
                    if PermissionBackend().has_perm(get_current_authenticated_user(),
                                                    "member:add_membership", empty_membership):  # If the user has right
                        t = format_html(t + ' <a class="btn btn-warning" href="{url}">{text}</a>',
                                        url=reverse_lazy('member:club_renew_membership',
                                                         kwargs={"pk": record.pk}), text=_("Renew"))
        return t

    def render_roles(self, record):
        roles = record.roles.all()
        s = ", ".join(str(role) for role in roles)
        if PermissionBackend().has_perm(get_current_authenticated_user(), "member.change_membership_roles", record):
            s = format_html("<a href='" + str(reverse_lazy("member:club_manage_roles", kwargs={"pk": record.pk}))
                            + "'>" + s + "</a>")
        return s

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover',
            'style': 'table-layout: fixed;'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('user', 'club', 'date_start', 'date_end', 'roles', 'fee', )
        model = Membership
