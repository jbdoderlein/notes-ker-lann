# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
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
    queryset = Invoice.objects.order_by('id')
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['bde', 'object', 'description', 'name', 'address', 'date', 'acquitted', 'locked', ]
    search_fields = ['$object', '$description', '$name', '$address', ]


class ProductViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Product` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/product/
    """
    queryset = Product.objects.order_by('invoice_id', 'id')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['invoice', 'designation', 'quantity', 'amount', ]
    search_fields = ['$designation', '$invoice__object', ]


class RemittanceTypeViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `RemittanceType` objects, serialize it to JSON with the given serializer
    then render it on /api/treasury/remittance_type/
    """
    queryset = RemittanceType.objects.order_by('id')
    serializer_class = RemittanceTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['note', ]
    search_fields = ['$note__special_type', ]


class RemittanceViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Remittance` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/remittance/
    """
    queryset = Remittance.objects.order_by('id')
    serializer_class = RemittanceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['date', 'remittance_type', 'comment', 'closed', 'transaction_proxies__transaction', ]
    search_fields = ['$remittance_type__note__special_type', '$comment', ]


class SogeCreditViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `SogeCredit` objects, serialize it to JSON with the given serializer,
    then render it on /api/treasury/soge_credit/
    """
    queryset = SogeCredit.objects.order_by('id')
    serializer_class = SogeCreditSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['user', 'user__last_name', 'user__first_name', 'user__email', 'user__note__alias__name',
                        'user__note__alias__normalized_name', 'transactions', 'credit_transaction', ]
    search_fields = ['$user__last_name', '$user__first_name', '$user__email', '$user__note__alias__name',
                     '$user__note__alias__normalized_name', ]
