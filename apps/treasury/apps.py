# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _


class TreasuryConfig(AppConfig):
    name = 'treasury'
    verbose_name = _('Treasury')

    def ready(self):
        """
        Define app internal signals to interact with other apps
        """

        from . import signals
        from note.models import SpecialTransaction
        from treasury.models import SpecialTransactionProxy
        post_save.connect(signals.save_special_transaction, sender=SpecialTransaction)

        # If the treasury app was disabled, we ensure that each special transaction is linked to a proxy
        for transaction in SpecialTransaction.objects.filter(specialtransactionproxy=None):
            SpecialTransactionProxy.objects.create(transaction=transaction, remittance=None)
