# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from api.viewsets import ReadProtectedModelViewSet
from .serializers import NoteSerializer, NotePolymorphicSerializer, NoteClubSerializer, NoteSpecialSerializer, \
    NoteUserSerializer, AliasSerializer, \
    TemplateCategorySerializer, TransactionTemplateSerializer, TransactionPolymorphicSerializer
from ..models.notes import Note, NoteClub, NoteSpecial, NoteUser, Alias
from ..models.transactions import TransactionTemplate, Transaction, TemplateCategory


class NoteViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Note` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/note/
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class NoteClubViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteClub` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/club/
    """
    queryset = NoteClub.objects.all()
    serializer_class = NoteClubSerializer


class NoteSpecialViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteSpecial` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/special/
    """
    queryset = NoteSpecial.objects.all()
    serializer_class = NoteSpecialSerializer


class NoteUserViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `NoteUser` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/user/
    """
    queryset = NoteUser.objects.all()
    serializer_class = NoteUserSerializer


class NotePolymorphicViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Note` objects (with polymorhism), serialize it to JSON with the given serializer,
    then render it on /api/note/note/
    """
    queryset = Note.objects.all()
    serializer_class = NotePolymorphicSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['$alias__normalized_name', '$alias__name', '$polymorphic_ctype__model', ]
    ordering_fields = ['alias__name', 'alias__normalized_name']

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested notes
        """
        queryset = super().get_queryset()

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
                queryset = queryset.filter(polymorphic_ctype__model="notespecial")
            else:
                queryset = queryset.none()

        return queryset.distinct()


class AliasViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Alias` objects, serialize it to JSON with the given serializer,
    then render it on /api/aliases/
    """
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['$normalized_name', '$name', '$note__polymorphic_ctype__model', ]
    ordering_fields = ['name', 'normalized_name']

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested aliases
        """

        queryset = super().get_queryset()

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


class TemplateCategoryViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TemplateCategory` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/category/
    """
    queryset = TemplateCategory.objects.all()
    serializer_class = TemplateCategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['$name', ]


class TransactionTemplateViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TransactionTemplate` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/template/
    """
    queryset = TransactionTemplate.objects.all()
    serializer_class = TransactionTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'amount', 'display', 'category', ]


class TransactionViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Transaction` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/transaction/
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionPolymorphicSerializer
    filter_backends = [SearchFilter]
    search_fields = ['$reason', ]
