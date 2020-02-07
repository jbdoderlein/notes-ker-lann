# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import NoteViewSet, NotePolymorphicViewSet, NoteClubViewSet, NoteUserViewSet, NoteSpecialViewSet, \
                            TransactionViewSet, TransactionTemplateViewSet, MembershipTransactionViewSet


def register_note_urls(router, path):
    """
    Configure router for Note REST API.
    """
    router.register(path + '', NotePolymorphicViewSet)

    router.register(path + '/transaction/transaction', TransactionViewSet)
    router.register(path + '/transaction/template', TransactionTemplateViewSet)
    router.register(path + '/transaction/membership', MembershipTransactionViewSet)
