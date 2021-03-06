# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later
import sys
from functools import lru_cache
from time import time

from django.contrib.sessions.models import Session
from note_kfet.middlewares import get_current_request


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
        # if settings.DEBUG:
        #     # Don't memoize in DEBUG mode
        #     return f(*args, **kwargs)

        nonlocal last_collect

        if "test" in sys.argv:
            # In a test environment, don't memoize permissions
            return f(*args, **kwargs)

        if time() - last_collect > 60:
            # Clear cache
            collect()
            last_collect = time()

        # If there is no session, then we don't memoize anything.
        request = get_current_request()
        if request is None or request.session is None or request.session.session_key is None:
            return f(*args, **kwargs)

        sess_key = request.session.session_key
        if sess_key not in sess_funs:
            # lru_cache makes the job of memoization
            # We store only the 512 latest data per session. It has to be enough.
            sess_funs[sess_key] = lru_cache(512)(f)
        try:
            return sess_funs[sess_key](*args, **kwargs)
        except TypeError:  # For add permissions, objects are not hashable (not yet created). Don't memoize this case.
            return f(*args, **kwargs)

    func.func_name = f.__name__

    return func
