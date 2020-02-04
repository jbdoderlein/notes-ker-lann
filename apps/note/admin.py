# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin, \
    PolymorphicChildModelFilter, PolymorphicParentModelAdmin

from .models.notes import Alias, Note, NoteClub, NoteSpecial, NoteUser
from .models.transactions import Transaction, TransactionCategory, TransactionTemplate


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
    list_display = ('pretty', 'balance', 'is_active')
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
    search_fields = ('club',)
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


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin customisation for Transaction
    """
    list_display = ('created_at', 'poly_source', 'poly_destination',
                    'quantity', 'amount', 'transaction_type', 'valid')
    list_filter = ('transaction_type', 'valid')
    autocomplete_fields = ('source', 'destination',)

    def poly_source(self, obj):
        """
        Force source to resolve polymorphic object
        """
        return str(obj.source)

    poly_source.short_description = _('source')

    def poly_destination(self, obj):
        """
        Force destination to resolve polymorphic object
        """
        return str(obj.destination)

    poly_destination.short_description = _('destination')

    def get_readonly_fields(self, request, obj=None):
        """
        Only valid can be edited after creation
        Else the amount of money would not be transferred
        """
        if obj:  # user is editing an existing object
            return 'created_at', 'source', 'destination', 'quantity',\
                   'amount', 'transaction_type'
        return []


@admin.register(TransactionTemplate)
class TransactionTemplateAdmin(admin.ModelAdmin):
    """
    Admin customisation for TransactionTemplate
    """
    list_display = ('name', 'poly_destination', 'amount', 'template_type')
    list_filter = ('template_type',)
    autocomplete_fields = ('destination',)

    def poly_destination(self, obj):
        """
        Force destination to resolve polymorphic object
        """
        return str(obj.destination)

    poly_destination.short_description = _('destination')


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    """
    Admin customisation for TransactionTemplate
    """
    list_display = ('name',)
    list_filter = ('name',)
