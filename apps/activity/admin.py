# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin

from .models import Activity, ActivityType, Guest


class ActivityAdmin(admin.ModelAdmin):
    """
    Admin customisation for Activity
    """
    list_display = ('name', 'activity_type', 'organizer')
    list_filter = ('activity_type', )
    search_fields = ['name', 'organizer__name']

    # Organize activities by start date
    date_hierarchy = 'date_start'
    ordering = ['-date_start']


class ActivityTypeAdmin(admin.ModelAdmin):
    """
    Admin customisation for ActivityType
    """
    list_display = ('name', 'can_invite', 'guest_entry_fee')


# Register your models here.
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityType, ActivityTypeAdmin)
admin.site.register(Guest)
