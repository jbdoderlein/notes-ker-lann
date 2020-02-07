# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import ActivityTypeViewSet, ActivityViewSet, GuestViewSet


def register_activity_urls(router, path):
    """
    Configure router for Activity REST API.
    """
    router.register(path + r'activity', ActivityViewSet)
    router.register(path + r'type', ActivityTypeViewSet)
    router.register(path + r'guest', GuestViewSet)
