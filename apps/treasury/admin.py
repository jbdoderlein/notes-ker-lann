# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-lateré

from django.contrib import admin
from note_kfet.admin import admin_site

from .forms import ProductForm
from .models import RemittanceType, Remittance, SogeCredit, Invoice, Product


@admin.register(RemittanceType, site=admin_site)
class RemittanceTypeAdmin(admin.ModelAdmin):
    """
    Admin customisation for RemiitanceType
    """
    list_display = ('note', )


@admin.register(Remittance, site=admin_site)
class RemittanceAdmin(admin.ModelAdmin):
    """
    Admin customisation for Remittance
    """
    list_display = ('remittance_type', 'date', 'comment', 'count', 'amount', 'closed', )

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        return not obj.closed and super().has_change_permission(request, obj)


@admin.register(SogeCredit, site=admin_site)
class SogeCreditAdmin(admin.ModelAdmin):
    """
    Admin customisation for Remittance
    """
    list_display = ('user', 'valid',)
    readonly_fields = ('transactions', 'credit_transaction',)

    def has_add_permission(self, request):
        # Don't create a credit manually
        return False


class ProductInline(admin.StackedInline):
    """
    Inline product in invoice admin
    """
    model = Product
    form = ProductForm


@admin.register(Invoice, site=admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin customisation for Invoice
    """
    list_display = ('object', 'id', 'bde', 'name', 'date', 'acquitted',)
    inlines = (ProductInline,)
