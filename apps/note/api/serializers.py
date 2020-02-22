# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from ..models.notes import Note, NoteClub, NoteSpecial, NoteUser, Alias
from ..models.transactions import TransactionTemplate, Transaction, MembershipTransaction


class NoteSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Notes.
    The djangorestframework plugin will analyse the model `Note` and parse all fields in the API.
    """
    class Meta:
        model = Note
        fields = '__all__'
        extra_kwargs = {
            'url': {
                'view_name': 'project-detail',
                'lookup_field': 'pk'
            },
        }


class NoteClubSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Club's notes.
    The djangorestframework plugin will analyse the model `NoteClub` and parse all fields in the API.
    """
    class Meta:
        model = NoteClub
        fields = '__all__'


class NoteSpecialSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for special notes.
    The djangorestframework plugin will analyse the model `NoteSpecial` and parse all fields in the API.
    """
    class Meta:
        model = NoteSpecial
        fields = '__all__'


class NoteUserSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for User's notes.
    The djangorestframework plugin will analyse the model `NoteUser` and parse all fields in the API.
    """
    class Meta:
        model = NoteUser
        fields = '__all__'


class AliasSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Aliases.
    The djangorestframework plugin will analyse the model `Alias` and parse all fields in the API.
    """
    class Meta:
        model = Alias
        fields = '__all__'


class NotePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Note: NoteSerializer,
        NoteUser: NoteUserSerializer,
        NoteClub: NoteClubSerializer,
        NoteSpecial: NoteSpecialSerializer
    }


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


class MembershipTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Membership transactions.
    The djangorestframework plugin will analyse the model `MembershipTransaction` and parse all fields in the API.
    """
    class Meta:
        model = MembershipTransaction
        fields = '__all__'
