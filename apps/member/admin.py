# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from note_kfet.admin import admin_site

from .forms import ProfileForm
from .models import Club, Membership, Profile


class ProfileInline(admin.StackedInline):
    """
    Inline user profile in user admin
    """
    model = Profile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile',)
    form = ProfileForm

    def get_inline_instances(self, request, obj=None):
        """
        When creating a new user don't show profile one the first step
        """
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Update Django User with profile
admin_site.register(User, CustomUserAdmin)

# Add other models
admin_site.register(Club)
admin_site.register(Membership)
