# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import InvoiceSerializer, ProductSerializer, RemittanceTypeSerializer, RemittanceSerializer,\
    SogeCreditSerializer
from ..models import Invoice, Product, RemittanceType, Remittance, SogeCredit


class InvoiceViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Invoice` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/invoice/
    """
    queryset = Invoice.objects.order_by("id").all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bde', ]


class ProductViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Product` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/product/
    """
    queryset = Product.objects.order_by("invoice_id", "id").all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$designation', ]


class RemittanceTypeViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `RemittanceType` objects, serialize it to JSON with the given serializer
    then render it on /api/treasury/remittance_type/
    """
    queryset = RemittanceType.objects.order_by("id")
    serializer_class = RemittanceTypeSerializer


class RemittanceViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Remittance` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/remittance/
    """
    queryset = Remittance.objects.order_by("id")
    serializer_class = RemittanceSerializer


class SogeCreditViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `SogeCredit` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/soge_credit/
    """
    queryset = SogeCredit.objects.order_by("id")
    serializer_class = SogeCreditSerializer
