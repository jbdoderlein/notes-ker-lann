# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import RedirectView
from note.models import Alias
from permission.backends import PermissionBackend


class IndexView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        """
        Calculate the index page according to the roles.
        A normal user will have access to the transfer page.
        A non-Kfet member will have access to its user detail page.
        The user "note" will display the consumption interface.
        """
        user = self.request.user

        # The account note will have the consumption page as default page
        if not PermissionBackend.check_perm(user, "auth.view_user", user):
            return reverse("note:consos")

        # People that can see the alias BDE are Kfet members
        if PermissionBackend.check_perm(user, "alias.view_alias", Alias.objects.get(name="BDE")):
            return reverse("note:transfer")

        # Non-Kfet members will don't see the transfer page, but their profile page
        return reverse("member:user_detail", args=(user.pk,))
