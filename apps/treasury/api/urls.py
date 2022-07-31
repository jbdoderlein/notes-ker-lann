# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import InvoiceViewSet, ProductViewSet, RemittanceViewSet, RemittanceTypeViewSet


def register_treasury_urls(router, path):
    """
    Configure router for treasury REST API.
    """
    router.register(path + '/invoice', InvoiceViewSet)
    router.register(path + '/product', ProductViewSet)
    router.register(path + '/remittance_type', RemittanceTypeViewSet)
    router.register(path + '/remittance', RemittanceViewSet)
