# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
from datetime import date

from django.forms import HiddenInput
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, TemplateView
from member.models import Membership

from .backends import PermissionBackend
from .models import Role


class ProtectQuerysetMixin:
    """
    This is a View class decorator and not a proper View class.
    Ensure that the user has the right to see or update objects.
    Display 404 error if the user can't see an object, remove the fields the user can't
    update on an update form (useful if the user can't change only specified fields).
    """
    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(PermissionBackend.filter_queryset(self.request.user, qs.model, "view")).distinct()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if not isinstance(self, UpdateView):
            return form

        # If we are in an UpdateView, we display only the fields the user has right to see.
        # No worry if the user change the hidden fields: a 403 error will be performed if the user tries to make
        # a custom request.
        # We could also delete the field, but some views might be affected.
        for key in form.base_fields:
            if not PermissionBackend.check_perm(self.request.user, "wei.change_weiregistration_" + key, self.object):
                form.fields[key].widget = HiddenInput()

        return form


class RightsView(TemplateView):
    template_name = "permission/all_rights.html"
    extra_context = {"title": _("Rights")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = _("All rights")
        roles = Role.objects.all()
        context["roles"] = roles
        if self.request.user.is_authenticated:
            active_memberships = Membership.objects.filter(user=self.request.user,
                                                           date_start__lte=date.today(),
                                                           date_end__gte=date.today()).all()
        else:
            active_memberships = Membership.objects.none()

        for role in roles:
            role.clubs = [membership.club for membership in active_memberships if role in membership.roles.all()]

        return context
