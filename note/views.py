# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


@login_required
def transfer(request):
    """
    Show transfer page

    TODO: If user have sufficient rights, they can transfer from an other note
    """
    return render(
        request,
        'note/transfer.html',
        {
            'title': _('Transfer money from your account to one or others')
        }
    )
