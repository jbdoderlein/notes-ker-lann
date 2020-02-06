# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .models.notes import Note, NoteClub, NoteSpecial, NoteUser
from .models.transactions import TransactionTemplate, Transaction, MembershipTransaction
from rest_framework import serializers, viewsets

class NoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Note
        fields = ('balance', 'is_active', 'display_image', 'created_at',)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class NoteClubSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NoteClub
        fields = ('balance', 'is_active', 'display_image', 'created_at', 'club',)


class NoteClubViewSet(viewsets.ModelViewSet):
    queryset = NoteClub.objects.all()
    serializer_class = NoteClubSerializer


class NoteSpecialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NoteSpecial
        fields = ('balance', 'is_active', 'display_image', 'created_at', 'club', 'special_type',)


class NoteSpecialViewSet(viewsets.ModelViewSet):
    queryset = NoteSpecial.objects.all()
    serializer_class = NoteSpecialSerializer


class NoteUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NoteUser
        fields = ('balance', 'is_active', 'display_image', 'created_at', 'user',)


class NoteUserViewSet(viewsets.ModelViewSet):
    queryset = NoteUser.objects.all()
    serializer_class = NoteUserSerializer


class TransactionTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TransactionTemplate
        fields = '__all__'


class TransactionTemplateViewSet(viewsets.ModelViewSet):
    queryset = TransactionTemplate.objects.all()
    serializer_class = TransactionTemplateSerializer


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class MembershipTransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MembershipTransaction
        fields = '__all__'


class MembershipTransactionViewSet(viewsets.ModelViewSet):
    queryset = MembershipTransaction.objects.all()
    serializer_class = MembershipTransactionSerializer
