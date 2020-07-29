# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-lateré

from django.contrib import admin

from note_kfet.admin import admin_site
from .models import RemittanceType, Remittance, SogeCredit


@admin.register(RemittanceType, site=admin_site)
class RemittanceTypeAdmin(admin.ModelAdmin):
    """
    Admin customisation for RemiitanceType
    """
    list_display = ('note', )


@admin.register(Remittance, site=admin_site)
class RemittanceAdmin(admin.ModelAdmin):
    """
    Admin customisation for Remittance
    """
    list_display = ('remittance_type', 'date', 'comment', 'count', 'amount', 'closed', )

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        return not obj.closed and super().has_change_permission(request, obj)


admin_site.register(SogeCredit)
