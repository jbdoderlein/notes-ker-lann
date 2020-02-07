# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import ProfileViewSet, ClubViewSet, RoleViewSet, MembershipViewSet


def register_members_urls(router, path):
    """
    Configure router for Member REST API.
    """
    router.register(path + r'profile', ProfileViewSet)
    router.register(path + r'club', ClubViewSet)
    router.register(path + r'role', RoleViewSet)
    router.register(path + r'membership', MembershipViewSet)
