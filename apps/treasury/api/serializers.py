# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from ..models import Invoice, Product


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
