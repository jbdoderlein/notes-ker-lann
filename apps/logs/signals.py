# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Changelog


def get_request_in_signal(sender):
    req = None
    for entry in reversed(inspect.stack()):
        try:
            req = entry[0].f_locals['request']
            # Check if there is a user
            # noinspection PyStatementEffect
            req.user
            break
        except:
            pass

    if not req:
        print("WARNING: Attempt to save " + str(sender) + " with no user")

    return req


def get_user_and_ip(sender):
    req = get_request_in_signal(sender)
    try:
        user = req.user
        if 'HTTP_X_FORWARDED_FOR' in req.META:
            ip = req.META.get('HTTP_X_FORWARDED_FOR')
        else:
            ip = req.META.get('REMOTE_ADDR')
    except:
        user = None
        ip = None
    return user, ip


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

@receiver(post_save)
def save_object(sender, instance, **kwargs):
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    previous = sender.objects.filter(pk=instance.pk).all()

    user, ip = get_user_and_ip(sender)

    previous_json = serializers.serialize('json', previous)[1:-1] if previous.exists else None
    instance_json = serializers.serialize('json', [instance, ])[1:-1]
    Changelog.objects.create(user=user,
                             ip=ip,
                             model=ContentType.objects.get_for_model(instance),
                             instance_pk=instance.pk,
                             previous=previous_json,
                             data=instance_json,
                             action=("edit" if previous.exists() else "create")
                             ).save()


@receiver(post_delete)
def delete_object(sender, instance, **kwargs):
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    user, ip = get_user_and_ip(sender)

    instance_json = serializers.serialize('json', [instance, ])[1:-1]
    Changelog.objects.create(user=user,
                             ip=ip,
                             model=ContentType.objects.get_for_model(instance),
                             instance_pk=instance.pk,
                             previous=instance_json,
                             data=None,
                             action="delete"
                             ).save()
