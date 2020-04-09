# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from permission.backends import PermissionBackend


class ProtectQuerysetMixin:
    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)

        return qs.filter(PermissionBackend.filter_queryset(self.request.user, qs.model, "view"))
