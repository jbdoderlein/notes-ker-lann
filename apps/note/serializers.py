# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .models.notes import Note, NoteClub, NoteSpecial, NoteUser
from .models.transactions import TransactionTemplate, Transaction, MembershipTransaction
from rest_framework import serializers, viewsets

class NoteSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Notes.
    The djangorestframework plugin will analyse the model `Note` and parse all fields in the API.
    """
    class Meta:
        model = Note
        fields = ('balance', 'is_active', 'display_image', 'created_at',)


class NoteViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Note` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/note/
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class NoteClubSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Club's notes.
    The djangorestframework plugin will analyse the model `NoteClub` and parse all fields in the API.
    """
    class Meta:
        model = NoteClub
        fields = ('balance', 'is_active', 'display_image', 'created_at', 'club',)


class NoteClubViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteClub` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/club/
    """
    queryset = NoteClub.objects.all()
    serializer_class = NoteClubSerializer


class NoteSpecialSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for special notes.
    The djangorestframework plugin will analyse the model `NoteSpecial` and parse all fields in the API.
    """
    class Meta:
        model = NoteSpecial
        fields = ('balance', 'is_active', 'display_image', 'created_at', 'club', 'special_type',)


class NoteSpecialViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteSpecial` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/special/
    """
    queryset = NoteSpecial.objects.all()
    serializer_class = NoteSpecialSerializer


class NoteUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for User's notes.
    The djangorestframework plugin will analyse the model `NoteUser` and parse all fields in the API.
    """
    class Meta:
        model = NoteUser
        fields = ('balance', 'is_active', 'display_image', 'created_at', 'user',)


class NoteUserViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteUser` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/user/
    """
    queryset = NoteUser.objects.all()
    serializer_class = NoteUserSerializer


class TransactionTemplateSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Transaction templates.
    The djangorestframework plugin will analyse the model `TransactionTemplate` and parse all fields in the API.
    """
    class Meta:
        model = TransactionTemplate
        fields = '__all__'


class TransactionTemplateViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TransactionTemplate` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/template/
    """
    queryset = TransactionTemplate.objects.all()
    serializer_class = TransactionTemplateSerializer


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Transactions.
    The djangorestframework plugin will analyse the model `Transaction` and parse all fields in the API.
    """
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Transaction` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/transaction/
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class MembershipTransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    REST API Serializer for Membership transactions.
    The djangorestframework plugin will analyse the model `MembershipTransaction` and parse all fields in the API.
    """
    class Meta:
        model = MembershipTransaction
        fields = '__all__'


class MembershipTransactionViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `MembershipTransaction` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/membership/
    """
    queryset = MembershipTransaction.objects.all()
    serializer_class = MembershipTransactionSerializer
