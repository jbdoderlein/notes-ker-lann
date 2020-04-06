# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later


def save_user_note(instance, raw, **_kwargs):
    """
    Hook to create and save a note when an user is updated
    """
    if raw:
        # When provisionning data, do not try to autocreate
        return

    if (instance.is_superuser or instance.profile.registration_valid) and instance.is_active:
        # Create note only when the registration is validated
        from note.models import NoteUser
        NoteUser.objects.get_or_create(user=instance)
        instance.note.save()


def save_club_note(instance, created, raw, **_kwargs):
    """
    Hook to create and save a note when a club is updated
    """
    if raw:
        # When provisionning data, do not try to autocreate
        return

    if created:
        from .models import NoteClub
        NoteClub.objects.create(club=instance)
    instance.note.save()
