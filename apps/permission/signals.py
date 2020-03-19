# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import PermissionDenied
from note_kfet.middlewares import get_current_authenticated_user


EXCLUDED = [
    'cas_server.proxygrantingticket',
    'cas_server.proxyticket',
    'cas_server.serviceticket',
    'cas_server.user',
    'cas_server.userattributes',
    'contenttypes.contenttype',
    'logs.changelog',
    'migrations.migration',
    'note.note',
    'note.noteuser',
    'note.noteclub',
    'note.notespecial',
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
        if user.has_perm(app_label + ".change_" + model_name, instance):
            return

        previous = qs.get()
        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(previous, field.name)
            new_value = getattr(instance, field.name)
            if old_value == new_value:
                continue
            if not user.has_perm(app_label + ".change_" + model_name + "_" + field_name, instance):
                raise PermissionDenied
    else:
        if not user.has_perm(app_label + ".add_" + model_name, instance):
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

    if not user.has_perm(app_label + ".delete_" + model_name, instance):
        raise PermissionDenied
