# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-lateré

from django.contrib import admin

from note_kfet.admin import admin_site
from .models import Permission, PermissionMask, Role


@admin.register(PermissionMask, site=admin_site)
class PermissionMaskAdmin(admin.ModelAdmin):
    """
    Admin customisation for PermissionMask
    """
    list_display = ('description', 'rank', )


@admin.register(Permission, site=admin_site)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin customisation for Permission
    """
    list_display = ('type', 'model', 'field', 'mask', 'description', )


@admin.register(Role, site=admin_site)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin customisation for Role
    """
    list_display = ('name', )
