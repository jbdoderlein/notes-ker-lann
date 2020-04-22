# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers
from note.api.serializers import SpecialTransactionSerializer

from ..models import Invoice, Product, RemittanceType, Remittance, SogeCredit


class ProductSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Product types.
    The djangorestframework plugin will analyse the model `Product` and parse all fields in the API.
    """

    class Meta:
        model = Product
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Invoice types.
    The djangorestframework plugin will analyse the model `Invoice` and parse all fields in the API.
    """
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('bde',)

    products = serializers.SerializerMethodField()

    def get_products(self, obj):
        return serializers.ListSerializer(child=ProductSerializer())\
            .to_representation(Product.objects.filter(invoice=obj).all())


class RemittanceTypeSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for RemittanceType types.
    The djangorestframework plugin will analyse the model `RemittanceType` and parse all fields in the API.
    """

    class Meta:
        model = RemittanceType
        fields = '__all__'


class RemittanceSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Remittance types.
    The djangorestframework plugin will analyse the model `Remittance` and parse all fields in the API.
    """

    transactions = serializers.SerializerMethodField()

    class Meta:
        model = Remittance
        fields = '__all__'

    def get_transactions(self, obj):
        return serializers.ListSerializer(child=SpecialTransactionSerializer()).to_representation(obj.transactions)


class SogeCreditSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for SogeCredit types.
    The djangorestframework plugin will analyse the model `SogeCredit` and parse all fields in the API.
    """

    class Meta:
        model = SogeCredit
        fields = '__all__'
