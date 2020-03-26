# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import stringfilter
from django import template
from note_kfet.middlewares import get_current_authenticated_user, get_current_session
from permission.backends import PermissionBackend


@stringfilter
def not_empty_model_list(model_name):
    """
    Return True if and only if the current user has right to see any object of the given model.
    """
    user = get_current_authenticated_user()
    session = get_current_session()
    if user is None:
        return False
    elif user.is_superuser and session.get("permission_mask", 0) >= 42:
        return True
    if session.get("not_empty_model_list_" + model_name, None):
        return session.get("not_empty_model_list_" + model_name, None) == 1
    spl = model_name.split(".")
    ct = ContentType.objects.get(app_label=spl[0], model=spl[1])
    qs = ct.model_class().objects.filter(PermissionBackend.filter_queryset(user, ct, "view")).all()
    session["not_empty_model_list_" + model_name] = 1 if qs.exists() else 2
    return session.get("not_empty_model_list_" + model_name) == 1


@stringfilter
def not_empty_model_change_list(model_name):
    """
    Return True if and only if the current user has right to change any object of the given model.
    """
    user = get_current_authenticated_user()
    session = get_current_session()
    if user is None:
        return False
    elif user.is_superuser and session.get("permission_mask", 0) >= 42:
        return True
    if session.get("not_empty_model_change_list_" + model_name, None):
        return session.get("not_empty_model_change_list_" + model_name, None) == 1
    spl = model_name.split(".")
    ct = ContentType.objects.get(app_label=spl[0], model=spl[1])
    qs = ct.model_class().objects.filter(PermissionBackend.filter_queryset(user, ct, "change"))
    session["not_empty_model_change_list_" + model_name] = 1 if qs.exists() else 2
    return session.get("not_empty_model_change_list_" + model_name) == 1


register = template.Library()
register.filter('not_empty_model_list', not_empty_model_list)
register.filter('not_empty_model_change_list', not_empty_model_change_list)
