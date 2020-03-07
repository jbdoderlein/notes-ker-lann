import functools
import json
import operator

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class InstancedPermission:

    def __init__(self, model, query, type, field):
        self.model = model
        self.query = query
        self.type = type
        self.field = field

    def applies(self, obj, permission_type, field_name=None):
        """
        Returns True if the permission applies to
        the field `field_name` object `obj`
        """
        if self.type == 'add':
            if permission_type == self.type:
                return self.query(obj)
        if ContentType.objects.get_for_model(obj) != self.model:
            # The permission does not apply to the model
            return False
        if self.permission is None:
            if permission_type == self.type:
                if field_name is not None:
                    return field_name == self.field
                else:
                    return True
            else:
                return False
        elif obj in self.model.objects.get(self.query):
            return True
        else:
            return False

    def __repr__(self):
        if self.field:
            return _("Can {type} {model}.{field} in {permission}").format(type=self.type, model=self.model, field=self.field, permission=self.permission)
        else:
            return _("Can {type} {model} in {permission}").format(type=self.type, model=self.model, permission=self.permission)


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
    #  query -> ['AND', query, …]            AND multiple queries
    #         | ['OR', query, …]             OR multiple queries
    #         | ['NOT', query]               Opposite of query
    #  query -> {key: value, …}              A list of fields and values of a Q object
    #  key   -> string                       A field name
    #  value -> int | string | bool | null   Literal values
    #         | [parameter]                  A parameter
    #         | {'F': oper}                  An F object
    #  oper  -> [string]                     A parameter
    #         | ['ADD', oper, …]             Sum multiple F objects or literal
    #         | ['SUB', oper, oper]          Substract two F objects or literal
    #         | ['MUL', oper, …]             Multiply F objects or literals
    #         | int | string | bool | null   Literal values
    #         | ['F', string]                A field
    #
    # Examples:
    #  Q(is_admin=True)  := {'is_admin': ['TYPE', 'bool', 'True']}
    #  ~Q(is_admin=True) := ['NOT', {'is_admin': ['TYPE', 'bool', 'True']}]
    query = models.TextField()

    type = models.CharField(max_length=15, choices=PERMISSION_TYPES)

    field = models.CharField(max_length=255, blank=True)

    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('model', 'query', 'type', 'field')

    def clean(self):
        if self.field and self.type not in {'view', 'change'}:
            raise ValidationError(_("Specifying field applies only to view and change permission types."))

    def save(self):
        self.full_clean()
        super().save()

    @staticmethod
    def compute_f(_oper, **kwargs):
        oper = _oper
        if isinstance(oper, list):
            if len(oper) == 1:
                return kwargs[oper[0]].pk
            elif len(oper) >= 2:
                if oper[0] == 'ADD':
                    return functools.reduce(operator.add, [compute_f(oper, **kwargs) for oper in oper[1:]])
                elif oper[0] == 'SUB':
                    return compute_f(oper[1], **kwargs) - compute_f(oper[2], **kwargs)
                elif oper[0] == 'MUL':
                    return functools.reduce(operator.mul, [compute_f(oper, **kwargs) for oper in oper[1:]])
                elif oper[0] == 'F':
                    return F(oper[1])
        else:
            return oper
        # TODO: find a better way to crash here
        raise Exception("F is wrong")

    def _about(_self, _query, **kwargs):
        self = _self
        query = _query
        if self.type == 'add'):
            # Handle add permission differently
            return self._about_add(query, **kwargs)
        if len(query) == 0:
            # The query is either [] or {} and
            # applies to all objects of the model
            # to represent this we return None
            return None
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
                    # It is a parameter we query its primary key
                    q_kwargs[key] = kwargs[value[0]].pk
                elif isinstance(value, dict):
                    # It is an F object
                    q_kwargs[key] = compute_f(query['F'], **kwargs)
                else:
                    q_kwargs[key] = value
            return Q(**q_kwargs)
        else:
            # TODO: find a better way to crash here
            raise Exception("query {} is wrong".format(self.query))

    def _about_add(_self, _query, **kwargs):
        self = _self
        query = _query
        if len(query) == 0:
            return lambda _: True
        if isinstance(query, list):
            if query[0] == 'AND':
                return lambda obj: functools.reduce(operator.and_, [self._about_add(query, **kwargs)(obj) for query in query[1:]])
            elif query[0] == 'OR':
                return lambda obj: functools.reduce(operator.or_, [self._about_add(query, **kwargs)(obj) for query in query[1:]])
            elif query[0] == 'NOT':
                return lambda obj: not self._about_add(query[1], **kwargs)(obj)
        elif isinstance(query, dict):
            q_kwargs = {}
            for key in query:
                value = query[key]
                if isinstance(value, list):
                    # It is a parameter we query its primary key
                    q_kwargs[key] = kwargs[value[0]].pk
                elif isinstance(value, dict):
                    # It is an F object
                    q_kwargs[key] = compute_f(query['F'], **kwargs)
                else:
                    q_kwargs[key] = value
            def func(obj):
                nonlocal q_kwargs
                for arg in q_kwargs:
                    if getattr(obj, arg) != q_kwargs(arg):
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
        return InstancedPermission(self.model, query, self.type, self.field)

    def __str__(self):
        if self.field:
            return _("Can {type} {model}.{field} in {query}").format(type=self.type, model=self.model, field=self.field, query=self.query)
        else:
            return _("Can {type} {model} in {query}").format(type=self.type, model=self.model, query=self.query)


class UserPermission(models.Model):

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

