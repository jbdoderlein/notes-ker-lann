# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import hashlib

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import constant_time_compare


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

    def verify(self, password, encoded):
        if '|' in encoded:
            salt, db_hashed_pass = encoded.split('$')[2].split('|')
            return constant_time_compare(hashlib.sha256((salt + password).encode("utf-8")).hexdigest(), db_hashed_pass)
        return super().verify(password, encoded)
