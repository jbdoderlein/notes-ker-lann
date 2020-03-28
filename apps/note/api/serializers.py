# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from ..models.notes import Note, NoteClub, NoteSpecial, NoteUser, Alias
from ..models.transactions import TransactionTemplate, Transaction, MembershipTransaction, TemplateCategory, \
    RecurrentTransaction, SpecialTransaction


class NoteSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Notes.
    The djangorestframework plugin will analyse the model `Note` and parse all fields in the API.
    """

    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = [f.name for f in model._meta.get_fields()]  # Notes are read-only protected


class NoteClubSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Club's notes.
    The djangorestframework plugin will analyse the model `NoteClub` and parse all fields in the API.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = NoteClub
        fields = '__all__'
        read_only_fields = ('note', 'club', )

    def get_name(self, obj):
        return str(obj)


class NoteSpecialSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for special notes.
    The djangorestframework plugin will analyse the model `NoteSpecial` and parse all fields in the API.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = NoteSpecial
        fields = '__all__'
        read_only_fields = ('note', )

    def get_name(self, obj):
        return str(obj)


class NoteUserSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for User's notes.
    The djangorestframework plugin will analyse the model `NoteUser` and parse all fields in the API.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = NoteUser
        fields = '__all__'
        read_only_fields = ('note', 'user', )

    def get_name(self, obj):
        return str(obj)


class AliasSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Aliases.
    The djangorestframework plugin will analyse the model `Alias` and parse all fields in the API.
    """

    class Meta:
        model = Alias
        fields = '__all__'

    def validate(self, attrs):
        instance = Alias(**attrs)
        instance.clean()
        return attrs


class NotePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Note: NoteSerializer,
        NoteUser: NoteUserSerializer,
        NoteClub: NoteClubSerializer,
        NoteSpecial: NoteSpecialSerializer
    }

    class Meta:
        model = Note

class ConsumerSerializer(serializers.ModelSerializer):
    """
    REST API Nested Serializer for Consumers.
    return Alias, and the note Associated to it in 
    """
    note = NotePolymorphicSerializer()
    class Meta:
        model = Alias
        fields = '__all__'

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('note')
    

class TemplateCategorySerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transaction templates.
    The djangorestframework plugin will analyse the model `TemplateCategory` and parse all fields in the API.
    """

    class Meta:
        model = TemplateCategory
        fields = '__all__'


class TransactionTemplateSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transaction templates.
    The djangorestframework plugin will analyse the model `TransactionTemplate` and parse all fields in the API.
    """

    class Meta:
        model = TransactionTemplate
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transactions.
    The djangorestframework plugin will analyse the model `Transaction` and parse all fields in the API.
    """

    class Meta:
        model = Transaction
        fields = '__all__'


class RecurrentTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transactions.
    The djangorestframework plugin will analyse the model `RecurrentTransaction` and parse all fields in the API.
    """

    class Meta:
        model = RecurrentTransaction
        fields = '__all__'


class MembershipTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Membership transactions.
    The djangorestframework plugin will analyse the model `MembershipTransaction` and parse all fields in the API.
    """

    class Meta:
        model = MembershipTransaction
        fields = '__all__'


class SpecialTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Special transactions.
    The djangorestframework plugin will analyse the model `SpecialTransaction` and parse all fields in the API.
    """

    class Meta:
        model = SpecialTransaction
        fields = '__all__'


class TransactionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Transaction: TransactionSerializer,
        RecurrentTransaction: RecurrentTransactionSerializer,
        MembershipTransaction: MembershipTransactionSerializer,
        SpecialTransaction: SpecialTransactionSerializer,
    }

    class Meta:
        model = Transaction
