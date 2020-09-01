# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.html import format_html
from django_tables2 import A
from member.models import Membership
from note_kfet.middlewares import get_current_authenticated_user
from permission.backends import PermissionBackend


class RightsTable(tables.Table):
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

    def render_club(self, value):
        # If the user has the right, link the displayed user with the page of its detail.
        s = value.name
        if PermissionBackend.check_perm(get_current_authenticated_user(), "member.view_club", value):
            s = format_html("<a href={url}>{name}</a>",
                            url=reverse_lazy('member:club_detail', kwargs={"pk": value.pk}), name=s)

        return s

    def render_roles(self, record):
        # If the user has the right to manage the roles, display the link to manage them
        roles = record.roles.filter((~(Q(name="Adhérent BDE")
                                     | Q(name="Adhérent Kfet")
                                     | Q(name="Membre de club")
                                     | Q(name="Bureau de club"))
                                     & Q(weirole__isnull=True))).all()
        s = ", ".join(str(role) for role in roles)
        if PermissionBackend.check_perm(get_current_authenticated_user(), "member.change_membership_roles", record):
            s = format_html("<a href='" + str(reverse_lazy("member:club_manage_roles", kwargs={"pk": record.pk}))
                            + "'>" + s + "</a>")
        return s

    class Meta:
        attrs = {
            'class': 'table table-condensed table-striped table-hover',
            'style': 'table-layout: fixed;'
        }
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('user__last_name', 'user.first_name', 'user', 'club', 'roles', )
        model = Membership


class SuperuserTable(tables.Table):
    username = tables.LinkColumn(
        "member:user_detail",
        args=[A("pk")],
    )

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'username', )
        attrs = {
            'class': 'table table-condensed table-striped table-hover',
            'style': 'table-layout: fixed;'
        }
