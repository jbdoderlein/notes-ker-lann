# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
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
from ..models.notes import Note, Alias, NoteUser, NoteClub, NoteSpecial
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
        user = self.request.user
        get_current_session().setdefault("permission_mask", 42)
        queryset = self.queryset.filter(PermissionBackend.filter_queryset(user, Note, "view")
                                        | PermissionBackend.filter_queryset(user, NoteUser, "view")
                                        | PermissionBackend.filter_queryset(user, NoteClub, "view")
                                        | PermissionBackend.filter_queryset(user, NoteSpecial, "view")).distinct()

        alias = self.request.query_params.get("alias", ".*")
        queryset = queryset.filter(
            Q(alias__name__iregex="^" + alias)
            | Q(alias__normalized_name__iregex="^" + Alias.normalize(alias))
            | Q(alias__normalized_name__iregex="^" + alias.lower())
        )

        return queryset.order_by("id")


class AliasViewSet(ReadProtectedModelViewSet):
    """
    REST API View set.
    The djangorestframework plugin will get all `Alias` objects, serialize it to JSON with the given serializer,
    then render it on /api/aliases/
    """
    queryset = Alias.objects
    serializer_class = AliasSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['$normalized_name', '$name', '$note__polymorphic_ctype__model', ]
    filterset_fields = ['note', 'note__noteuser__user', 'note__noteclub__club', 'note__polymorphic_ctype__model', ]
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
    filterset_fields = ['note', 'note__noteuser__user', 'note__noteclub__club', 'note__polymorphic_ctype__model', ]
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
        queryset = queryset.prefetch_related('note')

        if alias:
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
        user = self.request.user
        get_current_session().setdefault("permission_mask", 42)
        return self.model.objects.filter(PermissionBackend.filter_queryset(user, self.model, "view"))\
            .order_by("created_at", "id")
