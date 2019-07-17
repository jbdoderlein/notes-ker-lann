# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView

from .models import Transaction


class TransactionCreate(LoginRequiredMixin, CreateView):
    """
    Show transfer page

    TODO: If user have sufficient rights, they can transfer from an other note
    """
    model = Transaction
    fields = ('destination', 'amount', 'reason')

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Transfer money from your account '
                             'to one or others')
        return context
