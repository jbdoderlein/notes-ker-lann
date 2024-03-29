# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.sites.admin import Site, SiteAdmin

from member.views import CustomLoginView


class StrongAdminSite(AdminSite):
    def has_permission(self, request):
        """
        Authorize only staff that have the correct permission mask
        """
        return request.user.is_active and request.user.is_staff and request.session.get("permission_mask", -1) >= 42

    def login(self, request, extra_context=None):
        return CustomLoginView.as_view()(request)


# Instantiate admin site and register some defaults
admin_site = StrongAdminSite()
admin_site.register(Site, SiteAdmin)

# Add external apps model
if "oauth2_provider" in settings.INSTALLED_APPS:
    from oauth2_provider.models import Application, Grant, AccessToken, RefreshToken
    from oauth2_provider.admin import ApplicationAdmin, \
        GrantAdmin,  AccessTokenAdmin,  RefreshTokenAdmin
    admin_site.register(Application, ApplicationAdmin)
    admin_site.register(Grant, GrantAdmin)
    admin_site.register(AccessToken, AccessTokenAdmin)
    admin_site.register(RefreshToken, RefreshTokenAdmin)

if "django_htcpcp_tea" in settings.INSTALLED_APPS:
    from django_htcpcp_tea.admin import *
    from django_htcpcp_tea.models import *
    admin_site.register(Pot, PotAdmin)
    admin_site.register(TeaType, TeaTypeAdmin)
    admin_site.register(Addition, AdditionAdmin)

if "mailer" in settings.INSTALLED_APPS:
    from mailer.admin import *
    from mailer.models import *
    admin_site.register(Message, MessageAdmin)
    admin_site.register(DontSendEntry, DontSendEntryAdmin)
    admin_site.register(MessageLog, MessageLogAdmin)

if "rest_framework" in settings.INSTALLED_APPS:
    from rest_framework.authtoken.admin import *
    from rest_framework.authtoken.models import *
    admin_site.register(Token, TokenAdmin)

if "cas_server" in settings.INSTALLED_APPS:
    from cas_server.admin import *
    from cas_server.models import *
    admin_site.register(ServicePattern, ServicePatternAdmin)
    admin_site.register(FederatedIendityProvider, FederatedIendityProviderAdmin)
