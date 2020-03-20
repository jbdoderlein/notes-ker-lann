# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-lateré

from django.contrib import admin

from .models import Permission, PermissionMask, RolePermissions


@admin.register(PermissionMask)
class PermissionMaskAdmin(admin.ModelAdmin):
    """
    Admin customisation for PermissionMask
    """
    list_display = ('description', 'rank', )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin customisation for Permission
    """
    list_display = ('type', 'model', 'field', 'mask', 'description', )


@admin.register(RolePermissions)
class RolePermissionsAdmin(admin.ModelAdmin):
    """
    Admin customisation for RolePermissions
    """
    list_display = ('role', )

