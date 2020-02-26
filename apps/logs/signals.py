# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import Changelog


def get_user_in_signal(sender, **kwargs):
    user = None
    for entry in reversed(inspect.stack()):
        try:
            user = entry[0].f_locals['request'].user
            break
        except:
            pass

    if not user:
        print("WARNING: Attempt to save " + str(sender) + " with no user")

    return user

EXCLUDED = [
        'Changelog',
        'Migration',
        'Session',
    ]

@receiver(pre_save)
def save_object(sender, instance, **kwargs):
    model_name = sender.__name__
    if model_name in EXCLUDED:
        return

    previous = sender.objects.filter(pk=instance.pk).all()

    user = get_user_in_signal(sender, **kwargs)
    if previous.exists:
        previous_json = serializers.serialize('json', previous)[1:-1]
    else:
        previous_json = None
    instance_json = serializers.serialize('json', [instance, ],)[1:-1]
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
    if model_name in EXCLUDED:
        return

    user = get_user_in_signal(sender, **kwargs)
    instance_json = serializers.serialize('json', [instance, ])[1:-1]
    Changelog.objects.create(user=user,
                                        model=model_name,
                                        instance_pk=instance.pk,
                                        previous=instance_json,
                                        data=None,
                                        action="delete"
                                        ).save()
