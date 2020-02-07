# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from note.models.notes import Note, NoteClub, NoteSpecial, NoteUser
from note.models.transactions import TransactionTemplate, Transaction, MembershipTransaction
from .serializers import NoteSerializer, NoteClubSerializer, NoteSpecialSerializer, NoteUserSerializer, \
                        TransactionTemplateSerializer, TransactionSerializer, MembershipTransactionSerializer
from rest_framework import viewsets


class NoteViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Note` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/note/
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class NoteClubViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteClub` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/club/
    """
    queryset = NoteClub.objects.all()
    serializer_class = NoteClubSerializer


class NoteSpecialViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteSpecial` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/special/
    """
    queryset = NoteSpecial.objects.all()
    serializer_class = NoteSpecialSerializer


class NoteUserViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteUser` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/user/
    """
    queryset = NoteUser.objects.all()
    serializer_class = NoteUserSerializer


class TransactionTemplateViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TransactionTemplate` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/template/
    """
    queryset = TransactionTemplate.objects.all()
    serializer_class = TransactionTemplateSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Transaction` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/transaction/
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class MembershipTransactionViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `MembershipTransaction` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/membership/
    """
    queryset = MembershipTransaction.objects.all()
    serializer_class = MembershipTransactionSerializer
