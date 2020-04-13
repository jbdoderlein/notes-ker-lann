# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import WEIClubViewSet, BusViewSet, BusTeamViewSet


def register_wei_urls(router, path):
    """
    Configure router for Member REST API.
    """
    router.register(path + '/club', WEIClubViewSet)
    router.register(path + '/bus', BusViewSet)
    router.register(path + '/team', BusTeamViewSet)
