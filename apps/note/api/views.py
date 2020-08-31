# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from api.viewsets import ReadProtectedModelViewSet, ReadOnlyProtectedModelViewSet
from note_kfet.middlewares import get_current_session
from permission.backends import PermissionBackend

from .serializers import NotePolymorphicSerializer, AliasSerializer, ConsumerSerializer,\
    TemplateCategorySerializer, TransactionTemplateSerializer, TransactionPolymorphicSerializer
from ..models.notes import Note, Alias
from ..models.transactions import TransactionTemplate, Transaction, TemplateCategory


class NotePolymorphicViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Note` objects (with polymorhism), serialize it to JSON with the given serializer,
    then render it on /api/note/note/
    """
    queryset = Note.objects.all()
    serializer_class = NotePolymorphicSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['polymorphic_ctype', 'is_active', ]
    search_fields = ['$alias__normalized_name', '$alias__name', '$polymorphic_ctype__model', ]
    ordering_fields = ['alias__name', 'alias__normalized_name']

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested notes
        """
        queryset = super().get_queryset().distinct()

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            Q(alias__name__iregex="^" + alias)
            | Q(alias__normalized_name__iregex="^" + Alias.normalize(alias))
            | Q(alias__normalized_name__iregex="^" + alias.lower())
        )

        return queryset


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

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method in ['PUT', 'PATCH']:
            # alias owner cannot be change once establish
            setattr(serializer_class.Meta, 'read_only_fields', ('note',))
        return serializer_class

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ValidationError as e:
            print(e)
            return Response({e.code: e.message}, status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested aliases
        """

        queryset = super().get_queryset()

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            name__iregex="^" + alias
        ).union(
            queryset.filter(
                Q(normalized_name__iregex="^" + Alias.normalize(alias))
                & ~Q(name__iregex="^" + alias)
            ),
            all=True).union(
            queryset.filter(
                Q(normalized_name__iregex="^" + alias.lower())
                & ~Q(normalized_name__iregex="^" + Alias.normalize(alias))
                & ~Q(name__iregex="^" + alias)
            ),
            all=True)

        return queryset


class ConsumerViewSet(ReadOnlyProtectedModelViewSet):
    queryset = Alias.objects.all()
    serializer_class = ConsumerSerializer
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
        queryset = queryset.order_by('name').prefetch_related('note')
        # We match first an alias if it is matched without normalization,
        # then if the normalized pattern matches a normalized alias.
        queryset = queryset.filter(
            name__iregex="^" + alias
        ).union(
            queryset.filter(
                Q(normalized_name__iregex="^" + Alias.normalize(alias))
                & ~Q(name__iregex="^" + alias)
            ),
            all=True).union(
            queryset.filter(
                Q(normalized_name__iregex="^" + alias.lower())
                & ~Q(normalized_name__iregex="^" + Alias.normalize(alias))
                & ~Q(name__iregex="^" + alias)
            ),
            all=True)

        return queryset.distinct()


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


class TransactionTemplateViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TransactionTemplate` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/template/
    """
    queryset = TransactionTemplate.objects.all()
    serializer_class = TransactionTemplateSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'amount', 'display', 'category', ]
    search_fields = ['$name', ]


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

    def get_queryset(self):
        user = self.request.user
        get_current_session().setdefault("permission_mask", 42)
        return self.model.objects.filter(PermissionBackend.filter_queryset(user, self.model, "view"))\
            .order_by("created_at", "id")
