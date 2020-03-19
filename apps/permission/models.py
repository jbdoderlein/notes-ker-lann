# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
import json
import operator

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class InstancedPermission:

    def __init__(self, model, query, type, field, mask):
        self.model = model
        self.query = query
        self.type = type
        self.field = field
        self.mask = mask

    def applies(self, obj, permission_type, field_name=None):
        """
        Returns True if the permission applies to
        the field `field_name` object `obj`
        """

        if not isinstance(obj, self.model.model_class()):
            # The permission does not apply to the model
            return False

        if self.type == 'add':
            if permission_type == self.type:
                return self.query(obj)

        if permission_type == self.type:
            if self.field and field_name != self.field:
                return False
            return obj in self.model.model_class().objects.filter(self.query).all()
        else:
            return False

    def __repr__(self):
        if self.field:
            return _("Can {type} {model}.{field} in {query}").format(type=self.type, model=self.model, field=self.field, query=self.query)
        else:
            return _("Can {type} {model} in {query}").format(type=self.type, model=self.model, query=self.query)

    def __str__(self):
        return self.__repr__()


class PermissionMask(models.Model):
    rank = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name=_('rank'),
    )

    description = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('description'),
    )

    def __str__(self):
        return self.description


class Permission(models.Model):

    PERMISSION_TYPES = [
        ('add', 'add'),
        ('view', 'view'),
        ('change', 'change'),
        ('delete', 'delete')
    ]

    model = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+')

    # A json encoded Q object with the following grammar
    #  query -> [] | {}  (the empty query representing all objects)
    #  query -> ["AND", query, …]            AND multiple queries
    #         | ["OR", query, …]             OR multiple queries
    #         | ["NOT", query]               Opposite of query
    #  query -> {key: value, …}              A list of fields and values of a Q object
    #  key   -> string                       A field name
    #  value -> int | string | bool | null   Literal values
    #         | [parameter]                  A parameter
    #         | {"F": oper}                  An F object
    #  oper  -> [string]                     A parameter
    #         | ["ADD", oper, …]             Sum multiple F objects or literal
    #         | ["SUB", oper, oper]          Substract two F objects or literal
    #         | ["MUL", oper, …]             Multiply F objects or literals
    #         | int | string | bool | null   Literal values
    #         | ["F", string]                A field
    #
    # Examples:
    #  Q(is_superuser=True)  := {"is_superuser": true}
    #  ~Q(is_superuser=True) := ["NOT", {"is_superuser": true}]
    query = models.TextField()

    type = models.CharField(max_length=15, choices=PERMISSION_TYPES)

    mask = models.ForeignKey(
        PermissionMask,
        on_delete=models.PROTECT,
    )

    field = models.CharField(max_length=255, blank=True)

    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('model', 'query', 'type', 'field')

    def clean(self):
        self.query = json.dumps(json.loads(self.query))
        if self.field and self.type not in {'view', 'change'}:
            raise ValidationError(_("Specifying field applies only to view and change permission types."))

    def save(self, **kwargs):
        self.full_clean()
        super().save()

    @staticmethod
    def compute_f(oper, **kwargs):
        if isinstance(oper, list):
            if oper[0] == 'ADD':
                return functools.reduce(operator.add, [Permission.compute_f(oper, **kwargs) for oper in oper[1:]])
            elif oper[0] == 'SUB':
                return Permission.compute_f(oper[1], **kwargs) - Permission.compute_f(oper[2], **kwargs)
            elif oper[0] == 'MUL':
                return functools.reduce(operator.mul, [Permission.compute_f(oper, **kwargs) for oper in oper[1:]])
            elif oper[0] == 'F':
                return F(oper[1])
            else:
                field = kwargs[oper[0]]
                for i in range(1, len(oper)):
                    field = getattr(field, oper[i])
                return field
        else:
            return oper

    @staticmethod
    def compute_param(value, **kwargs):
        if not isinstance(value, list):
            return value

        field = kwargs[value[0]]
        for i in range(1, len(value)):
            if isinstance(value[i], list):
                field = getattr(field, value[i][0])
                params = []
                call_kwargs = {}
                for j in range(1, len(value[i])):
                    param = Permission.compute_param(value[i][j], **kwargs)
                    if isinstance(param, dict):
                        for key in param:
                            val = Permission.compute_param(param[key], **kwargs)
                            call_kwargs[key] = val
                    else:
                        params.append(param)
                field = field(*params, **call_kwargs)
            else:
                field = getattr(field, value[i])
        return field

    def _about(self, query, **kwargs):
        if self.type == 'add':
            # Handle add permission differently
            return self._about_add(query, **kwargs)
        if len(query) == 0:
            # The query is either [] or {} and
            # applies to all objects of the model
            # to represent this we return a trivial request
            return Q(pk=F("pk"))
        if isinstance(query, list):
            if query[0] == 'AND':
                return functools.reduce(operator.and_, [self._about(query, **kwargs) for query in query[1:]])
            elif query[0] == 'OR':
                return functools.reduce(operator.or_, [self._about(query, **kwargs) for query in query[1:]])
            elif query[0] == 'NOT':
                return ~self._about(query[1], **kwargs)
        elif isinstance(query, dict):
            q_kwargs = {}
            for key in query:
                value = query[key]
                if isinstance(value, list):
                    # It is a parameter we query its return value
                    q_kwargs[key] = Permission.compute_param(value, **kwargs)
                elif isinstance(value, dict):
                    # It is an F object
                    q_kwargs[key] = Permission.compute_f(value['F'], **kwargs)
                else:
                    q_kwargs[key] = value
            return Q(**q_kwargs)
        else:
            # TODO: find a better way to crash here
            raise Exception("query {} is wrong".format(self.query))

    def _about_add(self, _query, **kwargs):
        query = _query
        if len(query) == 0:
            return lambda _: True
        if isinstance(query, list):
            if query[0] == 'AND':
                return lambda obj: functools.reduce(operator.and_, [self._about_add(q, **kwargs)(obj) for q in query[1:]])
            elif query[0] == 'OR':
                return lambda obj: functools.reduce(operator.or_, [self._about_add(q, **kwargs)(obj) for q in query[1:]])
            elif query[0] == 'NOT':
                return lambda obj: not self._about_add(query[1], **kwargs)(obj)
        elif isinstance(query, dict):
            q_kwargs = {}
            for key in query:
                value = query[key]
                if isinstance(value, list):
                    # It is a parameter we query its primary key
                    q_kwargs[key] = Permission.compute_param(value, **kwargs)
                elif isinstance(value, dict):
                    # It is an F object
                    q_kwargs[key] = Permission.compute_f(query['F'], **kwargs)
                else:
                    q_kwargs[key] = value
            def func(obj):
                nonlocal q_kwargs
                for arg in q_kwargs:
                    spl = arg.split('__')
                    value = obj
                    last = None
                    for s in spl:
                        if not hasattr(obj, s):
                            last = s
                            break
                        value = getattr(obj, s)
                    if last == "lte":  # TODO Add more filters
                        if value > q_kwargs[arg]:
                            return False
                    elif value != q_kwargs[arg]:
                        return False
                return True
            return func

    def about(self, **kwargs):
        """
        Return an InstancedPermission with the parameters
        replaced by their values and the query interpreted
        """
        query = json.loads(self.query)
        query = self._about(query, **kwargs)
        return InstancedPermission(self.model, query, self.type, self.field, self.mask)

    def __str__(self):
        if self.field:
            return _("Can {type} {model}.{field} in {query}").format(type=self.type, model=self.model, field=self.field, query=self.query)
        else:
            return _("Can {type} {model} in {query}").format(type=self.type, model=self.model, query=self.query)


class UserPermission(models.Model):

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

