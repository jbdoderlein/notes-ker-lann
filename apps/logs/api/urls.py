# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import ChangelogViewSet


def register_logs_urls(router, path):
    """
    Configure router for Activity REST API.
    """
    router.register(path, ChangelogViewSet)
