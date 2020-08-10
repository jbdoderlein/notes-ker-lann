# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin
from note_kfet.admin import admin_site

from .models import Activity, ActivityType, Entry, Guest


@admin.register(Activity, site=admin_site)
class ActivityAdmin(admin.ModelAdmin):
    """
    Admin customisation for Activity
    """
    list_display = ('name', 'activity_type', 'organizer')
    list_filter = ('activity_type',)
    search_fields = ['name', 'organizer__name']

    # Organize activities by start date
    date_hierarchy = 'date_start'
    ordering = ['-date_start']


@admin.register(ActivityType, site=admin_site)
class ActivityTypeAdmin(admin.ModelAdmin):
    """
    Admin customisation for ActivityType
    """
    list_display = ('name', 'can_invite', 'guest_entry_fee')


@admin.register(Guest, site=admin_site)
class GuestAdmin(admin.ModelAdmin):
    """
    Admin customisation for Guest
    """
    list_display = ('last_name', 'first_name', 'activity', 'inviter')


@admin.register(Entry, site=admin_site)
class EntryAdmin(admin.ModelAdmin):
    """
    Admin customisation for Entry
    """
    list_display = ('note', 'activity', 'time', 'guest')
