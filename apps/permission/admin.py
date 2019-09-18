from django.contrib import admin

from .models import Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin customisation for Permission
    """
    list_display = ('type', 'model', 'field', 'permission')
