# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .views import NoteViewSet, NotePolymorphicViewSet, NoteClubViewSet, NoteUserViewSet, NoteSpecialViewSet, \
                            TransactionViewSet, TransactionTemplateViewSet, MembershipTransactionViewSet


def register_note_urls(router, path):
    """
    Configure router for Note REST API.
    """
    router.register(path + r'note', NotePolymorphicViewSet)
    router.register(path + r'club', NoteClubViewSet)
    router.register(path + r'user', NoteUserViewSet)
    router.register(path + r'special', NoteSpecialViewSet)

    router.register(path + r'transaction/transaction', TransactionViewSet)
    router.register(path + r'transaction/template', TransactionTemplateViewSet)
    router.register(path + r'transaction/membership', MembershipTransactionViewSet)
