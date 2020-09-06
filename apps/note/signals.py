# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later


def save_user_note(instance, raw, **_kwargs):
    """
    Hook to create and save a note when an user is updated
    """
    if not raw and (instance.is_superuser or instance.profile.registration_valid):
        # Create note only when the registration is validated
        from note.models import NoteUser
        NoteUser.objects.get_or_create(user=instance)
        instance.note.save()


def save_club_note(instance, raw, **_kwargs):
    """
    Hook to create and save a note when a club is updated
    """
    if raw:
        # When provisionning data, do not try to autocreate
        return

    from .models import NoteClub
    NoteClub.objects.get_or_create(club=instance)
    instance.note.save()


def delete_transaction(instance, **_kwargs):
    """
    Whenever we want to delete a transaction (caution with this), we ensure the transaction is invalid first.
    """
    instance.valid = False
    instance.save()
