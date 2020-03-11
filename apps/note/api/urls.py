# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import NotePolymorphicViewSet, AliasViewSet, \
    TemplateCategoryViewSet, TransactionViewSet, TransactionTemplateViewSet


def register_note_urls(router, path):
    """
    Configure router for Note REST API.
    """
    router.register(path + '/note', NotePolymorphicViewSet)
    router.register(path + '/alias', AliasViewSet)

    router.register(path + '/transaction/category', TemplateCategoryViewSet)
    router.register(path + '/transaction/transaction', TransactionViewSet)
    router.register(path + '/transaction/template', TransactionTemplateViewSet)
