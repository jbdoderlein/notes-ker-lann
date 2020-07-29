# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from note_kfet.admin import admin_site
from .models import WEIClub, WEIRegistration, WEIMembership, WEIRole, Bus, BusTeam

admin_site.register(WEIClub)
admin_site.register(WEIRegistration)
admin_site.register(WEIMembership)
admin_site.register(WEIRole)
admin_site.register(Bus)
admin_site.register(BusTeam)
