# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import Changelog


def get_request_in_signal(sender, **kwargs):
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


EXCLUDED = [
        'changelog',
        'migration',
        'revision',
        'session',
        'version',
    ]

@receiver(pre_save)
def save_object(sender, instance, **kwargs):
    model_name = sender.__name__
    if model_name.lower() in EXCLUDED:
        return

    previous = sender.objects.filter(pk=instance.pk).all()

    req = get_request_in_signal(sender, **kwargs)
    try:
        user = req.user
        if 'X-Real-Ip' in req.headers:
            ip = req.headers.get('X-Real-Ip')
        else:
            ip = req.headers.get('REMOTE_ADDR')
        print(ip)
        print(req.headers)
    except:
        user = None
        ip = None

    from rest_framework.renderers import JSONRenderer
    previous_json = JSONRenderer().render(previous)
    instance_json = JSONRenderer().render(instance)
    Changelog.objects.create(user=user,
                                        model=ContentType.objects.get_for_model(instance),
                                        instance_pk=instance.pk,
                                        previous=previous_json,
                                        data=instance_json,
                                        action=("edit" if previous.exists() else "create")
                                        )#.save()


@receiver(pre_delete)
def delete_object(sender, instance, **kwargs):
    model_name = sender.__name__
    if model_name.lower() in EXCLUDED:
        return

    req = get_request_in_signal(sender, **kwargs)
    try:
        user = req.user
        if 'X-Real-Ip' in req.headers:
            ip = req.headers.get('X-Real-Ip')
        else:
            ip = req.headers.get('REMOTE_ADDR')
        print(ip)
        print(req.headers)
    except:
        user = None
        ip = None

    instance_json = serializers.serialize('json', [instance, ])[1:-1]
    Changelog.objects.create(user=user,
                                        model=ContentType.objects.get_for_model(instance),
                                        instance_pk=instance.pk,
                                        previous=instance_json,
                                        data=None,
                                        action="delete"
                                        ).save()
