# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
import re

from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from api.viewsets import ReadProtectedModelViewSet, ReadOnlyProtectedModelViewSet
from permission.backends import PermissionBackend

from .serializers import NotePolymorphicSerializer, AliasSerializer, ConsumerSerializer,\
    TemplateCategorySerializer, TransactionTemplateSerializer, TransactionPolymorphicSerializer, \
    TrustSerializer
from ..models.notes import Note, Alias, NoteUser, NoteClub, NoteSpecial, Trust
from ..models.transactions import TransactionTemplate, Transaction, TemplateCategory


class NotePolymorphicViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Note` objects (with polymorhism),
    serialize it to JSON with the given serializer,
    then render it on /api/note/note/
    """
    queryset = Note.objects.order_by('id')
    serializer_class = NotePolymorphicSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['alias__name', 'polymorphic_ctype', 'is_active', 'balance', 'last_negative', 'created_at', ]
    search_fields = ['$alias__normalized_name', '$alias__name', '$polymorphic_ctype__model',
                     '$noteuser__user__last_name', '$noteuser__user__first_name', '$noteuser__user__email',
                     '$noteuser__user__email', '$noteclub__club__email', ]
    ordering_fields = ['alias__name', 'alias__normalized_name', 'balance', 'created_at', ]

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested notes
        """
        queryset = self.queryset.filter(PermissionBackend.filter_queryset(self.request, Note, "view")
                                        | PermissionBackend.filter_queryset(self.request, NoteUser, "view")
                                        | PermissionBackend.filter_queryset(self.request, NoteClub, "view")
                                        | PermissionBackend.filter_queryset(self.request, NoteSpecial, "view"))\
            .distinct()

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            Q(alias__name__iregex="^" + alias)
            | Q(alias__normalized_name__iregex="^" + Alias.normalize(alias))
            | Q(alias__normalized_name__iregex="^" + alias.lower())
        )

        return queryset.order_by("id")


class TrustViewSet(ReadProtectedModelViewSet):
    """
    REST Trust View set.
    The djangorestframework plugin will get all `Trust` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/trust/
    """
    queryset = Trust.objects
    serializer_class = TrustSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['$trusting__alias__name', '$trusting__alias__normalized_name',
            '$trusted__alias__name', '$trusted__alias__normalized_name']
    filterset_fields = ['trusting', 'trusting__noteuser__user', 'trusted', 'trusted__noteuser__user',]
    ordering_fields = ['trusting', 'trusted', ]

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method in ['PUT', 'PATCH']:
            # trust relationship can't change people involved
            serializer_class.Meta.read_only_fields = ('trusting', 'trusting',)
        return serializer_class

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ValidationError as e:
            return Response({e.code: str(e)}, status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AliasViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Alias` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/aliases/
    """
    queryset = Alias.objects
    serializer_class = AliasSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['$normalized_name', '$name', '$note__polymorphic_ctype__model', ]
    filterset_fields = ['name', 'normalized_name', 'note', 'note__noteuser__user',
                        'note__noteclub__club', 'note__polymorphic_ctype__model', ]
    ordering_fields = ['name', 'normalized_name', ]

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method in ['PUT', 'PATCH']:
            # alias owner cannot be change once establish
            serializer_class.Meta.read_only_fields = ('note',)
        return serializer_class

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ValidationError as e:
            return Response({e.code: str(e)}, status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested aliases
        """

        queryset = super().get_queryset().distinct()

        alias = self.request.query_params.get("alias", None)
        if alias:
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

        return queryset.order_by("name")


class ConsumerViewSet(ReadOnlyProtectedModelViewSet):
    queryset = Alias.objects
    serializer_class = ConsumerSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['$normalized_name', '$name', '$note__polymorphic_ctype__model', ]
    filterset_fields = ['name', 'normalized_name', 'note', 'note__noteuser__user',
                        'note__noteclub__club', 'note__polymorphic_ctype__model', ]
    ordering_fields = ['name', 'normalized_name', ]

    def get_queryset(self):
        """
        Parse query and apply filters.
        :return: The filtered set of requested aliases
        """

        queryset = super().get_queryset().distinct()
        # Sqlite doesn't support ORDER BY in subqueries
        queryset = queryset.order_by("name") \
            if settings.DATABASES[queryset.db]["ENGINE"] == 'django.db.backends.postgresql' else queryset

        alias = self.request.query_params.get("alias", None)
        # Check if this is a valid regex. If not, we won't check regex
        try:
            re.compile(alias)
            valid_regex = True
        except (re.error, TypeError):
            valid_regex = False
        suffix = '__iregex' if valid_regex else '__istartswith'
        alias_prefix = '^' if valid_regex else ''
        queryset = queryset.prefetch_related('note')

        if alias:
            # We match first an alias if it is matched without normalization,
            # then if the normalized pattern matches a normalized alias.
            queryset = queryset.filter(
                **{f'name{suffix}': alias_prefix + alias}
            ).union(
                queryset.filter(
                    Q(**{f'normalized_name{suffix}': alias_prefix + Alias.normalize(alias)})
                    & ~Q(**{f'name{suffix}': alias_prefix + alias})
                ),
                all=True).union(
                queryset.filter(
                    Q(**{f'normalized_name{suffix}': alias_prefix + alias.lower()})
                    & ~Q(**{f'normalized_name{suffix}': alias_prefix + Alias.normalize(alias)})
                    & ~Q(**{f'name{suffix}': alias_prefix + alias})
                ),
                all=True)

        queryset = queryset if settings.DATABASES[queryset.db]["ENGINE"] == 'django.db.backends.postgresql' \
            else queryset.order_by("name")

        return queryset.distinct()


class TemplateCategoryViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TemplateCategory` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/category/
    """
    queryset = TemplateCategory.objects.order_by('name')
    serializer_class = TemplateCategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'templates', 'templates__name']
    search_fields = ['$name', '$templates__name', ]


class TransactionTemplateViewSet(viewsets.ModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `TransactionTemplate` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/template/
    """
    queryset = TransactionTemplate.objects.order_by('name')
    serializer_class = TransactionTemplateSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name', 'amount', 'display', 'category', 'category__name', ]
    search_fields = ['$name', '$category__name', ]
    ordering_fields = ['amount', ]


class TransactionViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Transaction` objects, serialize it to JSON with the given serializer,
    then render it on /api/note/transaction/transaction/
    """
    queryset = Transaction.objects.order_by('-created_at')
    serializer_class = TransactionPolymorphicSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['source', 'source_alias', 'source__alias__name', 'source__alias__normalized_name',
                        'destination', 'destination_alias', 'destination__alias__name',
                        'destination__alias__normalized_name', 'quantity', 'polymorphic_ctype', 'amount',
                        'created_at', 'valid', 'invalidity_reason', ]
    search_fields = ['$reason', '$source_alias', '$source__alias__name', '$source__alias__normalized_name',
                     '$destination_alias', '$destination__alias__name', '$destination__alias__normalized_name',
                     '$invalidity_reason', ]
    ordering_fields = ['created_at', 'amount', ]

    def get_queryset(self):
        return self.model.objects.filter(PermissionBackend.filter_queryset(self.request, self.model, "view"))\
            .order_by("created_at", "id")
