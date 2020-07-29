# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.admin import AdminSite
from django.contrib.sites.admin import Site, SiteAdmin

from member.views import CustomLoginView
from .middlewares import get_current_session


class StrongAdminSite(AdminSite):
    def has_permission(self, request):
        """
        Authorize only staff that have the correct permission mask
        """
        session = get_current_session()
        return request.user.is_active and request.user.is_staff and session.get("permission_mask", -1) >= 42

    def login(self, request, extra_context=None):
        return CustomLoginView.as_view()(request)


# Instantiate admin site and register some defaults
admin_site = StrongAdminSite()
admin_site.register(Site, SiteAdmin)
