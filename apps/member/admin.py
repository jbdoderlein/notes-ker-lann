# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from note.templatetags.pretty_money import pretty_money
from note_kfet.admin import admin_site

from .forms import ProfileForm
from .models import Club, Membership, Profile


class ProfileInline(admin.StackedInline):
    """
    Inline user profile in user admin
    """
    model = Profile
    form = ProfileForm
    can_delete = False


@admin.register(User, site=admin_site)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile',)

    def get_inline_instances(self, request, obj=None):
        """
        When creating a new user don't show profile one the first step
        """
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(Club, site=admin_site)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_club', 'email', 'require_memberships', 'pretty_fee_paid',
                    'pretty_fee_unpaid', 'membership_start', 'membership_end',)
    ordering = ('name',)
    search_fields = ('name', 'email',)

    def pretty_fee_paid(self, obj):
        return pretty_money(obj.membership_fee_paid)

    def pretty_fee_unpaid(self, obj):
        return pretty_money(obj.membership_fee_unpaid)

    pretty_fee_paid.short_description = _("membership fee (paid students)")
    pretty_fee_unpaid.short_description = _("membership fee (unpaid students)")


@admin.register(Membership, site=admin_site)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'date_start', 'date_end', 'view_roles', 'pretty_fee',)
    ordering = ('-date_start', 'club')

    def view_roles(self, obj):
        return ", ".join(role.name for role in obj.roles.all())

    def pretty_fee(self, obj):
        return pretty_money(obj.fee)

    view_roles.short_description = _("roles")
    pretty_fee.short_description = _("fee")
