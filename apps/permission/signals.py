# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from note_kfet.middlewares import get_current_request
from permission.backends import PermissionBackend


EXCLUDED = [
    'cas_server.proxygrantingticket',
    'cas_server.proxyticket',
    'cas_server.serviceticket',
    'cas_server.user',
    'cas_server.userattributes',
    'contenttypes.contenttype',
    'logs.changelog',
    'migrations.migration',
    'oauth2_provider.accesstoken',
    'oauth2_provider.grant',
    'oauth2_provider.refreshtoken',
    'sessions.session',
]


def pre_save_object(sender, instance, **kwargs):
    """
    Before a model get saved, we check the permissions
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    if hasattr(instance, "_force_save") or hasattr(instance, "_no_signal"):
        return

    request = get_current_request()
    if request is None:
        # Action performed on shell is always granted
        return

    qs = sender.objects.filter(pk=instance.pk).all()
    model_name_full = instance._meta.label_lower.split(".")
    app_label = model_name_full[0]
    model_name = model_name_full[1]

    if qs.exists():
        # We check if the user can change the model

        # If the user has all right on a model, then OK
        if PermissionBackend.check_perm(request, app_label + ".change_" + model_name, instance):
            return

        # In the other case, we check if he/she has the right to change one field
        previous = qs.get()

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field.name)
            new_value = getattr(instance, field.name)
            # If the field wasn't modified, no need to check the permissions
            if old_value == new_value:
                continue
            if not PermissionBackend.check_perm(request, app_label + ".change_" + model_name + "_" + field_name,
                                                instance):
                raise PermissionDenied(
                    _("You don't have the permission to change the field {field} on this instance of model"
                      " {app_label}.{model_name}.")
                    .format(field=field_name, app_label=app_label, model_name=model_name, )
                )
    else:
        # We check if the user has right to add the object
        has_perm = PermissionBackend.check_perm(request, app_label + ".add_" + model_name, instance)

        if not has_perm:
            raise PermissionDenied(
                _("You don't have the permission to add an instance of model {app_label}.{model_name}.")
                .format(app_label=app_label, model_name=model_name, ))


def pre_delete_object(instance, **kwargs):
    """
    Before a model get deleted, we check the permissions
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    if hasattr(instance, "_force_delete") or hasattr(instance, "pk") and instance.pk == 0 \
            or hasattr(instance, "_no_signal"):
        # Don't check permissions on force-deleted objects
        return

    request = get_current_request()
    if request is None:
        # Action performed on shell is always granted
        return

    model_name_full = instance._meta.label_lower.split(".")
    app_label = model_name_full[0]
    model_name = model_name_full[1]

    # We check if the user has rights to delete the object
    if not PermissionBackend.check_perm(request, app_label + ".delete_" + model_name, instance):
        raise PermissionDenied(
            _("You don't have the permission to delete this instance of model {app_label}.{model_name}.")
            .format(app_label=app_label, model_name=model_name))
