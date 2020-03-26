# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from logs import signals as logs_signals
from note_kfet.middlewares import get_current_authenticated_user
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
    'sessions.session',
]


def pre_save_object(sender, instance, **kwargs):
    """
    Before a model get saved, we check the permissions
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    user = get_current_authenticated_user()
    if user is None:
        # Action performed on shell is always granted
        return

    qs = sender.objects.filter(pk=instance.pk).all()
    model_name_full = instance._meta.label_lower.split(".")
    app_label = model_name_full[0]
    model_name = model_name_full[1]

    if qs.exists():
        # We check if the user can change the model

        # If the user has all right on a model, then OK
        if PermissionBackend().has_perm(user, app_label + ".change_" + model_name, instance):
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
            if not PermissionBackend().has_perm(user, app_label + ".change_" + model_name + "_" + field_name, instance):
                raise PermissionDenied
    else:
        # We check if the user can add the model

        # While checking permissions, the object will be inserted in the DB, then removed.
        # We disable temporary the connectors
        pre_save.disconnect(pre_save_object)
        pre_delete.disconnect(pre_delete_object)
        # We disable also logs connectors
        pre_save.disconnect(logs_signals.pre_save_object)
        post_save.disconnect(logs_signals.save_object)
        post_delete.disconnect(logs_signals.delete_object)

        # We check if the user has right to add the object
        has_perm = PermissionBackend().has_perm(user, app_label + ".add_" + model_name, instance)

        # Then we reconnect all
        pre_save.connect(pre_save_object)
        pre_delete.connect(pre_delete_object)
        pre_save.connect(logs_signals.pre_save_object)
        post_save.connect(logs_signals.save_object)
        post_delete.connect(logs_signals.delete_object)

        if not has_perm:
            raise PermissionDenied


def pre_delete_object(sender, instance, **kwargs):
    """
    Before a model get deleted, we check the permissions
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    user = get_current_authenticated_user()
    if user is None:
        # Action performed on shell is always granted
        return

    model_name_full = instance._meta.label_lower.split(".")
    app_label = model_name_full[0]
    model_name = model_name_full[1]

    # We check if the user has rights to delete the object
    if not PermissionBackend().has_perm(user, app_label + ".delete_" + model_name, instance):
        raise PermissionDenied
