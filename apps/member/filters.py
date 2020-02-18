# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2018-2019 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django_filters import FilterSet, CharFilter
from django.contrib.auth.models import User
from django.db.models import CharField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'username', 'profile__section']
        filter_overrides = {
            CharField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains'
                }
            }
        }


class UserFilterFormHelper(FormHelper):
    form_method = 'GET'
    layout = Layout(
        'last_name',
        'first_name',
        'username',
        'profile__section',
        Submit('Submit', 'Apply Filter'),
    )
