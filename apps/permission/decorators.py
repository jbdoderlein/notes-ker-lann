# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache
from time import time

from django.contrib.sessions.models import Session
from note_kfet.middlewares import get_current_session


def memoize(f):
    """
    Memoize results and store in sessions

    This decorator is useful for permissions: they are loaded once needed, then stored for next calls.
    The storage is contained with sessions since it depends on the selected mask.
    """
    sess_funs = {}
    last_collect = time()

    def collect():
        """
        Clear cache of results when sessions are invalid, to flush useless data.
        This function is called every minute.
        """
        nonlocal sess_funs

        new_sess_funs = {}
        for sess_key in sess_funs:
            if Session.objects.filter(session_key=sess_key).exists():
                new_sess_funs[sess_key] = sess_funs[sess_key]
        sess_funs = new_sess_funs

    def func(*args, **kwargs):
        nonlocal last_collect

        if time() - last_collect > 60:
            # Clear cache
            collect()
            last_collect = time()

        # If there is no session, then we don't memoize anything.
        sess = get_current_session()
        if sess is None or sess.session_key is None:
            return f(*args, **kwargs)

        sess_key = sess.session_key
        if sess_key not in sess_funs:
            # lru_cache makes the job of memoization
            # We store only the 512 latest data per session. It has to be enough.
            sess_funs[sess_key] = lru_cache(512)(f)
        return sess_funs[sess_key](*args, **kwargs)

    func.func_name = f.__name__

    return func