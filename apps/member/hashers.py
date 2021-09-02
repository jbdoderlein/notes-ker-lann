# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import hashlib

from django.conf import settings
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import constant_time_compare
from note_kfet.middlewares import get_current_request


class CustomNK15Hasher(PBKDF2PasswordHasher):
    """
    Permet d'importer les mots de passe depuis la Note KFet 2015.
    Si un hash de mot de passe est de la forme :
    `custom_nk15$<NB>$<ENCODED>`
    où <NB> est un entier quelconque (symbolisant normalement un nombre d'itérations)
    et <ENCODED> le hash du mot de passe dans la Note Kfet 2015,
    alors ce hasher va vérifier le mot de passe.
    N'ayant pas la priorité (cf note_kfet/settings/base.py), le mot de passe sera
    converti automatiquement avec l'algorithme PBKDF2.
    """
    algorithm = "custom_nk15"

    def must_update(self, encoded):
        if settings.DEBUG:
            # Small hack to let superusers to impersonate people.
            # Don't change their password.
            request = get_current_request()
            current_user = request.user
            if current_user is not None and current_user.is_superuser:
                return False
        return True

    def verify(self, password, encoded):
        if settings.DEBUG:
            # Small hack to let superusers to impersonate people.
            # If a superuser is already connected, let him/her log in as another person.
            request = get_current_request()
            current_user = request.user
            if current_user is not None and current_user.is_superuser\
                    and request.session.get("permission_mask", -1) >= 42:
                return True

        if '|' in encoded:
            salt, db_hashed_pass = encoded.split('$')[2].split('|')
            return constant_time_compare(hashlib.sha256((salt + password).encode("utf-8")).hexdigest(), db_hashed_pass)
        return super().verify(password, encoded)


class DebugSuperuserBackdoor(PBKDF2PasswordHasher):
    """
    In debug mode and during the beta, superusers can login into other accounts for tests.
    """
    def must_update(self, encoded):
        return False

    def verify(self, password, encoded):
        if settings.DEBUG:
            # Small hack to let superusers to impersonate people.
            # If a superuser is already connected, let him/her log in as another person.
            request = get_current_request()
            current_user = request.user
            if current_user is not None and current_user.is_superuser\
                    and request.session.get("permission_mask", -1) >= 42:
                return True
        return super().verify(password, encoded)
