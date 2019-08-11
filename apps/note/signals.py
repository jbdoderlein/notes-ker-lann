# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later


def save_user_note(instance, created, **_kwargs):
    """
    Hook to create and save a note when an user is updated
    """
    if created:
        from .models import NoteUser
        NoteUser.objects.create(user=instance)
    instance.note.save()


def save_club_note(instance, created, **_kwargs):
    """
    Hook to create and save a note when a club is updated
    """
    if created:
        from .models import NoteClub
        NoteClub.objects.create(club=instance)
    instance.note.save()