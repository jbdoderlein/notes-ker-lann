# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date

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
    """
    List all clubs.
    """
    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        order_by = ('id',)
        model = Club
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('name', 'email',)
        order_by = ('name',)
        row_attrs = {
            'class': 'table-row',
            'id': lambda record: "row-" + str(record.pk),
            'data-href': lambda record: record.pk
        }


class UserTable(tables.Table):
    """
    List all users.
    """
    alias = tables.Column()

    section = tables.Column(accessor='profile.section')

    balance = tables.Column(accessor='note.balance', verbose_name=_("Balance"))

    def render_balance(self, record, value):
        return pretty_money(value)\
            if PermissionBackend.check_perm(get_current_authenticated_user(), "note.view_note", record.note) else "—"

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('last_name', 'first_name', 'username', 'alias', 'email')
        model = User
        row_attrs = {
            'class': 'table-row',
            'data-href': lambda record: record.pk
        }


class MembershipTable(tables.Table):
    """
    List all memberships.
    """
    roles = tables.Column(
        attrs={
            "td": {
                "class": "text-truncate",
            }
        }
    )

    def render_user(self, value):
        # If the user has the right, link the displayed user with the page of its detail.
        s = value.username
        if PermissionBackend.check_perm(get_current_authenticated_user(), "auth.view_user", value):
            s = format_html("<a href={url}>{name}</a>",
                            url=reverse_lazy('member:user_detail', kwargs={"pk": value.pk}), name=s)

        return s

    def render_club(self, value):
        # If the user has the right, link the displayed club with the page of its detail.
        s = value.name
        if PermissionBackend.check_perm(get_current_authenticated_user(), "member.view_club", value):
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
                        date_start=date.today(),
                        date_end=date.today(),
                        fee=0,
                    )
                    if PermissionBackend.check_perm(get_current_authenticated_user(),
                                                    "member:add_membership", empty_membership):  # If the user has right
                        t = format_html(t + ' <a class="btn btn-warning" href="{url}">{text}</a>',
                                        url=reverse_lazy('member:club_renew_membership',
                                                         kwargs={"pk": record.pk}), text=_("Renew"))
        return t

    def render_roles(self, record):
        # If the user has the right to manage the roles, display the link to manage them
        roles = record.roles.all()
        s = ", ".join(str(role) for role in roles)
        if PermissionBackend.check_perm(get_current_authenticated_user(), "member.change_membership_roles", record):
            s = format_html("<a href='" + str(reverse_lazy("member:club_manage_roles", kwargs={"pk": record.pk}))
                            + "'>" + s + "</a>")
        return s

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped',
            'style': 'table-layout: fixed;'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('user', 'club', 'date_start', 'date_end', 'roles', 'fee', )
        model = Membership


class ClubManagerTable(tables.Table):
    """
    List managers of a club.
    """

    def render_user(self, value):
        # If the user has the right, link the displayed user with the page of its detail.
        s = value.username
        if PermissionBackend.check_perm(get_current_authenticated_user(), "auth.view_user", value):
            s = format_html("<a href={url}>{name}</a>",
                            url=reverse_lazy('member:user_detail', kwargs={"pk": value.pk}), name=s)

        return s

    def render_roles(self, record):
        roles = record.roles.all()
        return ", ".join(str(role) for role in roles)

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover',
            'style': 'table-layout: fixed;'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('user', 'user.first_name', 'user.last_name', 'roles', )
        model = Membership
