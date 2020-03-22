# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin

from .models import Invoice, Product


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'object', 'acquitted', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('designation', 'quantity', 'amount', )
