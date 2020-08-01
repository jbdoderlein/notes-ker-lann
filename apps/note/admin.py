# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin, \
    PolymorphicChildModelFilter, PolymorphicParentModelAdmin
from note_kfet.admin import admin_site

from .models.notes import Alias, Note, NoteClub, NoteSpecial, NoteUser
from .models.transactions import Transaction, TemplateCategory, TransactionTemplate, \
    RecurrentTransaction, MembershipTransaction, SpecialTransaction
from .templatetags.pretty_money import pretty_money


class AliasInlines(admin.TabularInline):
    """
    Define user and club aliases when editing their note
    """
    extra = 0
    model = Alias


@admin.register(Note, site=admin_site)
class NoteAdmin(PolymorphicParentModelAdmin):
    """
    Parent regrouping all note types as children
    """
    child_models = (NoteClub, NoteSpecial, NoteUser)
    list_filter = (
        PolymorphicChildModelFilter,
        'is_active',
    )

    # Use a polymorphic list
    list_display = ('pretty', 'balance', 'is_active')
    polymorphic_list = True

    # Organize notes by registration date
    date_hierarchy = 'created_at'

    # Search by aliases
    search_fields = ['alias__name']


@admin.register(NoteClub, site=admin_site)
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


@admin.register(NoteSpecial, site=admin_site)
class NoteSpecialAdmin(PolymorphicChildModelAdmin):
    """
    Child for a special note, see NoteAdmin
    """
    readonly_fields = ('balance',)

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


@admin.register(NoteUser, site=admin_site)
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


@admin.register(Transaction, site=admin_site)
class TransactionAdmin(PolymorphicParentModelAdmin):
    """
    Admin customisation for Transaction
    """
    child_models = (Transaction, RecurrentTransaction, MembershipTransaction, SpecialTransaction)
    list_display = ('created_at', 'poly_source', 'poly_destination',
                    'quantity', 'amount', 'valid')
    list_filter = ('valid',)
    readonly_fields = (
        'source',
        'destination',
    )

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
            return 'created_at', 'source', 'destination', 'quantity', \
                   'amount'
        return []


@admin.register(MembershipTransaction, site=admin_site)
class MembershipTransactionAdmin(PolymorphicChildModelAdmin):
    """
    Admin customisation for MembershipTransaction
    """


@admin.register(RecurrentTransaction, site=admin_site)
class RecurrentTransactionAdmin(PolymorphicChildModelAdmin):
    """
    Admin customisation for RecurrentTransaction
    """


@admin.register(SpecialTransaction, site=admin_site)
class SpecialTransactionAdmin(PolymorphicChildModelAdmin):
    """
    Admin customisation for SpecialTransaction
    """


@admin.register(TransactionTemplate, site=admin_site)
class TransactionTemplateAdmin(admin.ModelAdmin):
    """
    Admin customisation for TransactionTemplate
    """
    list_display = ('name', 'poly_destination', 'pretty_amount', 'category', 'display', 'highlighted',)
    list_filter = ('category', 'display', 'highlighted',)
    search_fields = ('name', 'destination__club__name', 'amount',)
    autocomplete_fields = ('destination',)

    def poly_destination(self, obj):
        """
        Force destination to resolve polymorphic object
        """
        return str(obj.destination)

    poly_destination.short_description = _('destination')

    def pretty_amount(self, obj):
        return pretty_money(obj.amount)

    pretty_amount.short_description = _("amount")


@admin.register(TemplateCategory, site=admin_site)
class TemplateCategoryAdmin(admin.ModelAdmin):
    """
    Admin customisation for TransactionTemplate
    """
    list_display = ('name',)
