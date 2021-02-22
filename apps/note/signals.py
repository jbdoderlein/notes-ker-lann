# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils import timezone


def save_user_note(instance, raw, **_kwargs):
    """
    Hook to create and save a note when an user is updated
    """
    if not raw and (instance.is_superuser or instance.profile.registration_valid)\
            and not hasattr(instance, "_no_signal"):
        # Create note only when the registration is validated
        from note.models import NoteUser
        NoteUser.objects.get_or_create(user=instance)
        instance.note.save()


def save_club_note(instance, raw, **_kwargs):
    """
    Hook to create and save a note when a club is updated
    """
    # When provisionning data, do not try to autocreate
    if not raw and not hasattr(instance, "_no_signal"):
        from .models import NoteClub
        NoteClub.objects.get_or_create(club=instance)
        instance.note.save()


def pre_save_note(instance, raw, **_kwargs):
    if not raw and instance.pk and not hasattr(instance, "_no_signal") and instance.balance < 0:
        from note.models import Note
        old_note = Note.objects.get(pk=instance.pk)
        if old_note.balance >= 0:
            # Passage en négatif
            instance.last_negative = timezone.now()
            instance.send_mail_negative_balance()


def delete_transaction(instance, **_kwargs):
    """
    Whenever we want to delete a transaction (caution with this), we ensure the transaction is invalid first.
    """
    if not hasattr(instance, "_no_signal"):
        instance.valid = False
        instance._force_save = True
        instance.save()
