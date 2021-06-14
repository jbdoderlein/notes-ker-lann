# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import ActivityTypeViewSet, ActivityViewSet, EntryViewSet, GuestViewSet


def register_activity_urls(router, path):
    """
    Configure router for Activity REST API.
    """
    router.register(path + '/activity', ActivityViewSet)
    router.register(path + '/type', ActivityTypeViewSet)
    router.register(path + '/guest', GuestViewSet)
    router.register(path + '/entry', EntryViewSet)
