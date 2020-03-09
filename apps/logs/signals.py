# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .middlewares import get_current_authenticated_user, get_current_ip
from .models import Changelog


EXCLUDED = [
    'admin.logentry',
    'authtoken.token',
    'cas_server.user',
    'cas_server.userattributes',
    'contenttypes.contenttype',
    'logs.changelog',
    'migrations.migration',
    'note.noteuser',
    'note.noteclub',
    'note.notespecial',
    'sessions.session',
    'reversion.revision',
    'reversion.version',
]


@receiver(pre_save)
def pre_save_object(sender, instance, **kwargs):
    qs = sender.objects.filter(pk=instance.pk).all()
    if qs.exists():
        instance._previous = qs.get()
    else:
        instance._previous = None


@receiver(post_save)
def save_object(sender, instance, **kwargs):
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    print("LOGGING SOMETHING")

    previous = instance._previous

    user, ip = get_current_authenticated_user(), get_current_ip()

    if user is not None and instance._meta.label_lower == "auth.user" and previous:
        # Don't save last login modifications
        if instance.last_login != previous.last_login:
            return

    previous_json = serializers.serialize('json', [previous, ])[1:-1] if previous else None
    instance_json = serializers.serialize('json', [instance, ])[1:-1]

    if previous_json == instance_json:
        # No modification
        return

    Changelog.objects.create(user=user,
                             ip=ip,
                             model=ContentType.objects.get_for_model(instance),
                             instance_pk=instance.pk,
                             previous=previous_json,
                             data=instance_json,
                             action=("edit" if previous else "create")
                             ).save()


@receiver(post_delete)
def delete_object(sender, instance, **kwargs):
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    user, ip = get_current_authenticated_user(), get_current_ip()

    instance_json = serializers.serialize('json', [instance, ])[1:-1]
    Changelog.objects.create(user=user,
                             ip=ip,
                             model=ContentType.objects.get_for_model(instance),
                             instance_pk=instance.pk,
                             previous=instance_json,
                             data=None,
                             action="delete"
                             ).save()
