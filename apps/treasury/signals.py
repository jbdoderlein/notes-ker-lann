# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from treasury.models import SpecialTransactionProxy, RemittanceType


def save_special_transaction(instance, created, **kwargs):
    """
    When a special transaction is created, we create its linked proxy
    """

    if not hasattr(instance, "_no_signal"):
        if created and RemittanceType.objects.filter(
                note=instance.source if instance.is_credit() else instance.destination).exists():
            proxy = SpecialTransactionProxy(transaction=instance, remittance=None)
            proxy._force_save = True
            proxy.save()
