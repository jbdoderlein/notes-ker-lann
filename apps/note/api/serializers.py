# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from note_kfet.middlewares import get_current_authenticated_user
from ..models.notes import Note, NoteClub, NoteSpecial, NoteUser, Alias
from ..models.transactions import TransactionTemplate, Transaction, MembershipTransaction, TemplateCategory, \
    TemplateTransaction, SpecialTransaction


class NoteSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Notes.
    The djangorestframework plugin will analyse the model `Note` and parse all fields in the API.
    """

    class Meta:
        model = Note
        fields = '__all__'


class NoteClubSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Club's notes.
    The djangorestframework plugin will analyse the model `NoteClub` and parse all fields in the API.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = NoteClub
        fields = '__all__'

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

    def get_name(self, obj):
        return str(obj)


class AliasSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Aliases.
    The djangorestframework plugin will analyse the model `Alias` and parse all fields in the API.
    """
    note = serializers.SerializerMethodField()

    class Meta:
        model = Alias
        fields = '__all__'

    def get_note(self, alias):
        if get_current_authenticated_user().has_perm("note.view_note", alias.note):
            return NotePolymorphicSerializer().to_representation(alias.note)
        else:
            return alias.note.id


class NotePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Note: NoteSerializer,
        NoteUser: NoteUserSerializer,
        NoteClub: NoteClubSerializer,
        NoteSpecial: NoteSpecialSerializer
    }

    class Meta:
        model = Note


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


class TemplateTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transactions.
    The djangorestframework plugin will analyse the model `TemplateTransaction` and parse all fields in the API.
    """

    class Meta:
        model = TemplateTransaction
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
        TemplateTransaction: TemplateTransactionSerializer,
        MembershipTransaction: MembershipTransactionSerializer,
        SpecialTransaction: SpecialTransactionSerializer,
    }

    class Meta:
        model = Transaction
