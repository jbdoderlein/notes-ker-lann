#!/usr/bin/env python

# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from . import views

app_name = 'member'
urlpatterns = [
    path('signup/',views.SignUp.as_view(),name="signup")
]
