# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import InvoiceViewSet, ProductViewSet, RemittanceViewSet, RemittanceTypeViewSet, SogeCreditViewSet


def register_treasury_urls(router, path):
    """
    Configure router for treasury REST API.
    """
    router.register(path + '/invoice', InvoiceViewSet)
    router.register(path + '/product', ProductViewSet)
    router.register(path + '/remittance_type', RemittanceTypeViewSet)
    router.register(path + '/remittance', RemittanceViewSet)
    router.register(path + '/soge_credit', SogeCreditViewSet)
