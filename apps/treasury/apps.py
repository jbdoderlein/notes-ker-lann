# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.db.models import Q
from django.db.models.signals import post_save, post_migrate
from django.utils.translation import gettext_lazy as _


class TreasuryConfig(AppConfig):
    name = 'treasury'
    verbose_name = _('Treasury')

    def ready(self):
        """
        Define app internal signals to interact with other apps
        """

        from . import signals
        from note.models import SpecialTransaction, NoteSpecial
        from treasury.models import SpecialTransactionProxy
        post_save.connect(signals.save_special_transaction, sender=SpecialTransaction)

        def setup_specialtransactions_proxies(**kwargs):
            # If the treasury app was disabled for any reason during a certain amount of time,
            # we ensure that each special transaction is linked to a proxy
            for transaction in SpecialTransaction.objects.filter(
                    source__in=NoteSpecial.objects.filter(~Q(remittancetype=None)),
                    specialtransactionproxy=None,
            ):
                proxy = SpecialTransactionProxy(transaction=transaction, remittance=None)
                proxy._force_save = True
                proxy.save()

        post_migrate.connect(setup_specialtransactions_proxies, sender=SpecialTransactionProxy)
