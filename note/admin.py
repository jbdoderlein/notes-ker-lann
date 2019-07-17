# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, \
    PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models.notes import Alias, Note, NoteClub, NoteSpecial, NoteUser
from .models.transactions import MembershipTransaction, Transaction, \
    TransactionTemplate


class AliasInlines(admin.TabularInline):
    """
    Define user and club aliases when editing their note
    """
    extra = 0
    model = Alias


@admin.register(Note)
class NoteAdmin(PolymorphicParentModelAdmin):
    """
    Parent regrouping all note types as children
    """
    child_models = (NoteClub, NoteSpecial, NoteUser)
    list_filter = (PolymorphicChildModelFilter, 'is_active',)

    # Use a polymorphic list
    list_display = ('__str__', 'balance', 'is_active')
    polymorphic_list = True

    # Organize notes by registration date
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    # Search by aliases
    search_fields = ['alias__name']


@admin.register(NoteClub)
class NoteClubAdmin(PolymorphicChildModelAdmin):
    """
    Child for a club note, see NoteAdmin
    """
    inlines = (AliasInlines,)

    # We can't change club after creation or the balance
    readonly_fields = ('club', 'balance')

    def has_add_permission(self, request):
        """
        A club note should not be manually added
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        A club note should not be manually removed
        """
        return False


@admin.register(NoteSpecial)
class NoteSpecialAdmin(PolymorphicChildModelAdmin):
    """
    Child for a special note, see NoteAdmin
    """
    readonly_fields = ('balance',)


@admin.register(NoteUser)
class NoteUserAdmin(PolymorphicChildModelAdmin):
    """
    Child for an user note, see NoteAdmin
    """
    inlines = (AliasInlines,)

    # We can't change user after creation or the balance
    readonly_fields = ('user', 'balance')

    def has_add_permission(self, request):
        """
        An user note should not be manually added
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        An user note should not be manually removed
        """
        return False


@admin.register(TransactionTemplate)
class TransactionTemplateAdmin(admin.ModelAdmin):
    """
    Admin customisation for TransactionTemplate
    """
    list_display = ('name', 'destination', 'amount', 'template_type')
    list_filter = ('destination', 'template_type',)
    # autocomplete_fields = ('destination',)


# Register other models here.
admin.site.register(MembershipTransaction)
admin.site.register(Transaction)
