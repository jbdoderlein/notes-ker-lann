# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
# Copied from https://gitlab.crans.org/bombar/codeflix/-/blob/master/codeflix/codeflix/tokens.py

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Create a unique token generator to confirm email addresses.
    """
    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and some user state that's sure to change
        after an account validation to produce a token that invalidated when
        it's used:
        1. The user.profile.email_confirmed field will change upon an account
        validation.
        2. The last_login field will usually be updated very shortly after
           an account validation.
        Failing those things, settings.PASSWORD_RESET_TIMEOUT_DAYS eventually
        invalidates the token.
        """
        # Truncate microseconds so that tokens are consistent even if the
        # database doesn't support microseconds.
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return str(user.pk) + str(user.email) + str(user.profile.email_confirmed)\
               + str(login_timestamp) + str(timestamp)


email_validation_token = AccountActivationTokenGenerator()
