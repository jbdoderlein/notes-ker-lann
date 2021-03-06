# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import ProfileViewSet, ClubViewSet, MembershipViewSet


def register_members_urls(router, path):
    """
    Configure router for Member REST API.
    """
    router.register(path + '/profile', ProfileViewSet)
    router.register(path + '/club', ClubViewSet)
    router.register(path + '/membership', MembershipViewSet)
