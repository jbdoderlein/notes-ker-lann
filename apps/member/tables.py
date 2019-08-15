#!/usr/bin/env python

import django_tables2 as tables
from .models import Club


class ClubTable(tables.Table):
    class Meta:
        attrs = {'class':'table table-bordered table-condensed table-striped table-hover'}
        model = Club
        template_name = 'django_tables2/bootstrap.html'
        fields= ('id','name','email')
        row_attrs = {'class':'table-row',
                     'data-href': lambda record: record.pk }
