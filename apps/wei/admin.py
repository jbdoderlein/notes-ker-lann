# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin

from .models import WEIClub, WEIRegistration, WEIMembership, WEIRole, Bus, BusTeam

admin.site.register(WEIClub)
admin.site.register(WEIRegistration)
admin.site.register(WEIMembership)
admin.site.register(WEIRole)
admin.site.register(Bus)
admin.site.register(BusTeam)
