# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later


def save_user_profile(instance, created, raw, **_kwargs):
    """
    Hook to create and save a profile when an user is updated if it is not registered with the signup form
    """
    if not raw and created and instance.is_active and not hasattr(instance, "_no_signal"):
        from .models import Profile
        Profile.objects.get_or_create(user=instance)
        if instance.is_superuser:
            instance.profile.email_confirmed = True
            instance.profile.registration_valid = True
        instance.profile.save()
