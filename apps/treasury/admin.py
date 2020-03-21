# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib import admin

from treasury.models import Billing, Product


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'acquitted', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('designation', 'quantity', 'amount', )
