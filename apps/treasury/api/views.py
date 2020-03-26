# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from api.viewsets import ReadProtectedModelViewSet

from .serializers import InvoiceSerializer, ProductSerializer, RemittanceTypeSerializer, RemittanceSerializer
from ..models import Invoice, Product, RemittanceType, Remittance


class InvoiceViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Invoice` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/invoice/
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bde', ]


class ProductViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Product` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/product/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$designation', ]


class RemittanceTypeViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `RemittanceType` objects, serialize it to JSON with the given serializer
    then render it on /api/treasury/remittance_type/
    """
    queryset = RemittanceType.objects.all()
    serializer_class = RemittanceTypeSerializer


class RemittanceViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Remittance` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/remittance/
    """
    queryset = Remittance.objects.all()
    serializer_class = RemittanceSerializer