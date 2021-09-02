# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import stringfilter
from django import template
from note_kfet.middlewares import get_current_request

from ..backends import PermissionBackend


@stringfilter
def not_empty_model_list(model_name):
    """
    Return True if and only if the current user has right to see any object of the given model.
    """
    request = get_current_request()
    user = request.user
    session = request.session
    if user is None or not user.is_authenticated:
        return False
    elif user.is_superuser and session.get("permission_mask", -1) >= 42:
        return True
    qs = model_list(model_name)
    return qs.exists()


@stringfilter
def model_list(model_name, t="view", fetch=True):
    """
    Return the queryset of all visible instances of the given model.
    """
    request = get_current_request()
    user = request.user
    spl = model_name.split(".")
    ct = ContentType.objects.get(app_label=spl[0], model=spl[1])
    qs = ct.model_class().objects.filter(PermissionBackend.filter_queryset(request, ct, t))
    if user is None or not user.is_authenticated:
        return qs.none()
    if fetch:
        qs = qs.all()
    return qs


@stringfilter
def model_list_length(model_name, t="view"):
    """
    Return the length of queryset of all visible instances of the given model.
    """
    return model_list(model_name, t, False).count()


def has_perm(perm, obj):
    return PermissionBackend.check_perm(get_current_request(), perm, obj)


register = template.Library()
register.filter('not_empty_model_list', not_empty_model_list)
register.filter('model_list', model_list)
register.filter('model_list_length', model_list_length)
register.filter('has_perm', has_perm)
