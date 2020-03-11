# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from .serializers import NoteSerializer, NotePolymorphicSerializer, NoteClubSerializer, NoteSpecialSerializer, \
    NoteUserSerializer, AliasSerializer, \
    TemplateCategorySerializer, TransactionTemplateSerializer, TransactionPolymorphicSerializer
from ..models.notes import Note, NoteClub, NoteSpecial, NoteUser, Alias
from ..models.transactions import TransactionTemplate, Transaction, TemplateCategory


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


class NotePolymorphicViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Note` objects (with polymorhism), serialize it to JSON with the given serializer,
    then render it on /api/note/note/
    """
    queryset = Note.objects.all()
    serializer_class = NotePolymorphicSerializer

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested notes
        """
        queryset = Note.objects.all()

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            Q(alias__name__regex="^" + alias)
            | Q(alias__normalized_name__regex="^" + alias.lower()))

        note_type = self.request.query_params.get("type", None)
        if note_type:
            types = str(note_type).lower()
            if "user" in types:
                queryset = queryset.filter(polymorphic_ctype__model="noteuser")
            elif "club" in types:
                queryset = queryset.filter(polymorphic_ctype__model="noteclub")
            elif "special" in types:
                queryset = queryset.filter(
                    polymorphic_ctype__model="notespecial")
            else:
                queryset = queryset.none()

        return queryset


class AliasViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Alias` objects, serialize it to JSON with the given serializer,
    then render it on /api/aliases/
    """
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested aliases
        """

        queryset = Alias.objects.all()

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            Q(name__regex="^" + alias) | Q(normalized_name__regex="^" + alias.lower()))

        note_id = self.request.query_params.get("note", None)
        if note_id:
            queryset = queryset.filter(id=note_id)

        note_type = self.request.query_params.get("type", None)
        if note_type:
            types = str(note_type).lower()
            if "user" in types:
                queryset = queryset.filter(
                    note__polymorphic_ctype__model="noteuser")
            elif "club" in types:
                queryset = queryset.filter(
                    note__polymorphic_ctype__model="noteclub")
            elif "special" in types:
                queryset = queryset.filter(
                    note__polymorphic_ctype__model="notespecial")
            else:
                queryset = queryset.none()

        return queryset


class TemplateCategoryViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TemplateCategory` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/category/
    """
    queryset = TemplateCategory.objects.all()
    serializer_class = TemplateCategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['$name', ]


class TransactionTemplateViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TransactionTemplate` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/template/
    """
    queryset = TransactionTemplate.objects.all()
    serializer_class = TransactionTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'amount', 'display', 'category', ]


class TransactionViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Transaction` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/transaction/
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionPolymorphicSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$reason', ]
