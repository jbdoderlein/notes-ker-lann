# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-lateré

from django.contrib import admin
from note_kfet.admin import admin_site

from .forms import ProductForm
from .models import RemittanceType, Remittance, Invoice, Product


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
        return not obj or (not obj.closed and super().has_change_permission(request, obj))


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
