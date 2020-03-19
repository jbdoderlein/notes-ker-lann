# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import stringfilter

from note_kfet.middlewares import get_current_authenticated_user, get_current_session
from django import template

from member.backends import PermissionBackend


def has_perm(value):
    return get_current_authenticated_user().has_perm(value)


@stringfilter
def not_empty_model_list(model_name):
    user = get_current_authenticated_user()
    if user is None:
        return False
    elif user.is_superuser and get_current_session().get("permission_mask", 0) >= 42:
        return True
    spl = model_name.split(".")
    ct = ContentType.objects.get(app_label=spl[0], model=spl[1])
    qs = ct.model_class().objects.filter(PermissionBackend.filter_queryset(user, ct, "view"))
    return qs.exists()


@stringfilter
def not_empty_model_change_list(model_name):
    user = get_current_authenticated_user()
    if user is None:
        return False
    elif user.is_superuser and get_current_session().get("permission_mask", 0) >= 42:
        return True
    spl = model_name.split(".")
    ct = ContentType.objects.get(app_label=spl[0], model=spl[1])
    qs = ct.model_class().objects.filter(PermissionBackend.filter_queryset(user, ct, "change"))
    return qs.exists()


register = template.Library()
register.filter('has_perm', has_perm)
register.filter('not_empty_model_list', not_empty_model_list)
register.filter('not_empty_model_change_list', not_empty_model_change_list)
