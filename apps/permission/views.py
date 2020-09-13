# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import HiddenInput
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, TemplateView, CreateView
from member.models import Membership

from .backends import PermissionBackend
from .models import Role
from .tables import RightsTable, SuperuserTable


class ProtectQuerysetMixin:
    """
    This is a View class decorator and not a proper View class.
    Ensure that the user has the right to see or update objects.
    Display 404 error if the user can't see an object, remove the fields the user can't
    update on an update form (useful if the user can't change only specified fields).
    """
    def get_queryset(self, filter_permissions=True, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(PermissionBackend.filter_queryset(self.request.user, qs.model, "view")).distinct()\
            if filter_permissions else qs

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404 as e:
            try:
                super().get_object(self.get_queryset(filter_permissions=False))
                raise PermissionDenied()
            except Http404:
                raise e

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

    def form_valid(self, form):
        """
        Submit the form, if the page is a FormView.
        If a PermissionDenied exception is raised, catch the error and display it at the top of the form.
        """
        try:
            return super().form_valid(form)
        except PermissionDenied:
            if isinstance(self, UpdateView):
                form.add_error(None, _("You don't have the permission to update this instance of the model \"{model}\""
                                       " with these parameters. Please correct your data and retry.")
                               .format(model=self.model._meta.verbose_name))
            else:
                form.add_error(None, _("You don't have the permission to create an instance of the model \"{model}\""
                                       " with these parameters. Please correct your data and retry.")
                               .format(model=self.model._meta.verbose_name))
            return self.form_invalid(form)


class ProtectedCreateView(LoginRequiredMixin, CreateView):
    """
    Extends a CreateView to check is the user has the right to create a sample instance of the given Model.
    If not, a 403 error is displayed.
    """

    def get_sample_object(self):
        """
        return a sample instance of the Model.
        It should be valid (can be stored properly in database), but must not collide with existing data.
        """
        raise NotImplementedError

    def dispatch(self, request, *args, **kwargs):
        # Check that the user is authenticated before that he/she has the permission to access here
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        model_class = self.model
        # noinspection PyProtectedMember
        app_label, model_name = model_class._meta.app_label, model_class._meta.model_name.lower()
        perm = app_label + ".add_" + model_name
        if not PermissionBackend.check_perm(request.user, perm, self.get_sample_object()):
            raise PermissionDenied(_("You don't have the permission to add an instance of model "
                                     "{app_label}.{model_name}.").format(app_label=app_label, model_name=model_name))
        return super().dispatch(request, *args, **kwargs)


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

        if self.request.user.is_authenticated:
            special_memberships = Membership.objects.filter(
                date_start__lte=date.today(),
                date_end__gte=date.today(),
            ).filter(roles__in=Role.objects.filter((~(Q(name="Adhérent BDE")
                                                      | Q(name="Adhérent Kfet")
                                                      | Q(name="Membre de club")
                                                      | Q(name="Bureau de club"))
                                                    & Q(weirole__isnull=True))))\
                .order_by("club__name", "user__last_name")\
                .distinct().all()
            context["special_memberships_table"] = RightsTable(special_memberships, prefix="clubs-")
            context["superusers"] = SuperuserTable(User.objects.filter(is_superuser=True).order_by("last_name").all(),
                                                   prefix="superusers-")

        return context
