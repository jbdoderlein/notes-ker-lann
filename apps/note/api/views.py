# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from api.viewsets import ReadProtectedModelViewSet, ReadOnlyProtectedModelViewSet
from member.backends import PermissionBackend
from .serializers import NotePolymorphicSerializer, AliasSerializer, TemplateCategorySerializer, \
    TransactionTemplateSerializer, TransactionPolymorphicSerializer
from ..models.notes import Note, Alias
from ..models.transactions import TransactionTemplate, Transaction, TemplateCategory


class NotePolymorphicViewSet(ReadOnlyProtectedModelViewSet):
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
        queryset = super().get_queryset().filter(PermissionBackend.filter_queryset(self.request.user, Note, "view"))

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            Q(alias__name__regex="^" + alias) | Q(alias__normalized_name__regex="^" + alias.lower()))

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

        queryset = super().get_queryset().filter(PermissionBackend.filter_queryset(self.request.user, Alias, "view"))

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            Q(name__regex="^" + alias) | Q(normalized_name__regex="^" + alias.lower()))

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
