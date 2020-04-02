# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import stringfilter
from django import template
from note.models import Transaction
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
    qs = model_list(model_name)
    return qs.exists()


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
    qs = model_list(model_name, "change")
    return qs.exists()


@stringfilter
def model_list(model_name, t="view"):
    """
    Return the queryset of all visible instances of the given model.
    """
    user = get_current_authenticated_user()
    if user is None:
        return False
    spl = model_name.split(".")
    ct = ContentType.objects.get(app_label=spl[0], model=spl[1])
    qs = ct.model_class().objects.filter(PermissionBackend.filter_queryset(user, ct, t)).all()
    return qs


def has_perm(perm, obj):
    return PermissionBackend.check_perm(get_current_authenticated_user(), perm, obj)


def can_create_transaction():
    """
    :return: True iff the authenticated user can create a transaction.
    """
    user = get_current_authenticated_user()
    session = get_current_session()
    if user is None:
        return False
    elif user.is_superuser and session.get("permission_mask", 0) >= 42:
        return True
    if session.get("can_create_transaction", None):
        return session.get("can_create_transaction", None) == 1

    empty_transaction = Transaction(
        source=user.note,
        destination=user.note,
        quantity=1,
        amount=0,
        reason="Check permissions",
    )
    session["can_create_transaction"] = PermissionBackend.check_perm(user, "note.add_transaction", empty_transaction)
    return session.get("can_create_transaction") == 1


register = template.Library()
register.filter('not_empty_model_list', not_empty_model_list)
register.filter('not_empty_model_change_list', not_empty_model_change_list)
register.filter('model_list', model_list)
register.filter('has_perm', has_perm)
