# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
import json
import operator
from copy import copy

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.db import models, transaction
from django.db.models import F, Q, Model
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _


class InstancedPermission:

    def __init__(self, model, query, type, field, mask, **kwargs):
        self.model = model
        self.raw_query = query
        self.query = None
        self.type = type
        self.field = field
        self.mask = mask
        self.kwargs = kwargs

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
                self.update_query()

                obj = copy(obj)
                obj.pk = 0
                with transaction.atomic():
                    sid = transaction.savepoint()
                    for o in self.model.model_class().objects.filter(pk=0).all():
                        o._force_delete = True
                        Model.delete(o)
                        # An object with pk 0 wouldn't deleted. That's not normal, we alert admins.
                        msg = "Lors de la vérification d'une permission d'ajout, un objet de clé primaire nulle était "\
                              "encore présent.\n"\
                              "Type de permission : " + self.type + "\n"\
                              "Modèle : " + str(self.model) + "\n"\
                              "Objet trouvé : " + str(model_to_dict(o)) + "\n\n"\
                              "--\nLe BDE"
                        mail_admins("[Note Kfet] Un objet a été supprimé de force", msg)

                    # Force insertion, no data verification, no trigger
                    obj._force_save = True
                    # We don't want to trigger any signal (log, ...)
                    obj._no_signal = True
                    Model.save(obj, force_insert=True)
                    ret = self.model.model_class().objects.filter(self.query & Q(pk=0)).exists()
                    # Delete testing object
                    obj._no_signal = True
                    obj._force_delete = True
                    Model.delete(obj)
                    transaction.savepoint_rollback(sid)

                return ret

        if permission_type == self.type:
            if self.field and field_name != self.field:
                return False
            self.update_query()
            return self.model.model_class().objects.filter(self.query & Q(pk=obj.pk)).exists()
        else:
            return False

    def update_query(self):
        """
        The query is not analysed in a first time. It is analysed at most once if needed.
        :return:
        """
        if not self.query:
            # noinspection PyProtectedMember
            self.query = Permission._about(self.raw_query, **self.kwargs)

    def __repr__(self):
        if self.field:
            return _("Can {type} {model}.{field} in {query}").format(type=self.type, model=self.model, field=self.field, query=self.query)
        else:
            return _("Can {type} {model} in {query}").format(type=self.type, model=self.model, query=self.query)

    def __str__(self):
        return self.__repr__()


class PermissionMask(models.Model):
    """
    Permissions that are hidden behind a mask
    """

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

    class Meta:
        verbose_name = _("permission mask")
        verbose_name_plural = _("permission masks")


class Permission(models.Model):

    PERMISSION_TYPES = [
        ('add', _('add')),
        ('view', _('view')),
        ('change', _('change')),
        ('delete', _('delete'))
    ]

    model = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name=_("model"),
    )

    # A json encoded Q object with the following grammar
    #  query -> [] | {}  (the empty query representing all objects)
    #  query -> ["AND", query, …]            AND multiple queries
    #         | ["OR", query, …]             OR multiple queries
    #         | ["NOT", query]               Opposite of query
    #  query -> {key: value, …}              A list of fields and values of a Q object
    #  key   -> string                       A field name
    #  value -> int | string | bool | null   Literal values
    #         | [parameter, …]               A parameter. See compute_param for more details.
    #         | {"F": oper}                  An F object
    #  oper  -> [string, …]                  A parameter. See compute_param for more details.
    #         | ["ADD", oper, …]             Sum multiple F objects or literal
    #         | ["SUB", oper, oper]          Substract two F objects or literal
    #         | ["MUL", oper, …]             Multiply F objects or literals
    #         | int | string | bool | null   Literal values
    #         | ["F", string]                A field
    #
    # Examples:
    #  Q(is_superuser=True)  := {"is_superuser": true}
    #  ~Q(is_superuser=True) := ["NOT", {"is_superuser": true}]
    query = models.TextField(
        verbose_name=_("query"),
    )

    type = models.CharField(
        max_length=15,
        choices=PERMISSION_TYPES,
        verbose_name=_("type"),
    )

    mask = models.ForeignKey(
        PermissionMask,
        on_delete=models.PROTECT,
        related_name="permissions",
        verbose_name=_("mask"),
    )

    field = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("field"),
    )

    permanent = models.BooleanField(
        default=False,
        help_text=_("Tells if the permission should be granted even if the membership of the user is expired."),
        verbose_name=_("permanent"),
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("description"),
    )

    class Meta:
        unique_together = ('model', 'query', 'type', 'field')
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")

    def clean(self):
        self.query = json.dumps(json.loads(self.query))
        if self.field and self.type not in {'view', 'change'}:
            raise ValidationError(_("Specifying field applies only to view and change permission types."))

    @transaction.atomic
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
        """
        A parameter is given by a list. The first argument is the name of the parameter.
        The parameters are the user, the club, and some classes (Note, ...)
        If there are more arguments in the list, then attributes are queried.
        For example, ["user", "note", "balance"] will return the balance of the note of the user.
        If an argument is a list, then this is interpreted with a function call:
            First argument is the name of the function, next arguments are parameters, and if there is a dict,
            then the dict is given as kwargs.
            For example: NoteUser.objects.filter(user__memberships__club__name="Kfet").all() is translated by:
            ["NoteUser", "objects", ["filter", {"user__memberships__club__name": "Kfet"}], ["all"]]
        """

        if not isinstance(value, list):
            return value

        field = kwargs[value[0]]
        for i in range(1, len(value)):
            if isinstance(value[i], list):
                if value[i][0] in kwargs:
                    field = Permission.compute_param(value[i], **kwargs)
                    continue

                if not hasattr(field, value[i][0]):
                    return False

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
                if not hasattr(field, value[i]):
                    return False

                field = getattr(field, value[i])
        return field

    @staticmethod
    def _about(query, **kwargs):
        """
        Translate JSON query into a Q query.
        :param query: The JSON query
        :param kwargs: Additional params
        :return: A Q object
        """
        if len(query) == 0:
            # The query is either [] or {} and
            # applies to all objects of the model
            # to represent this we return a trivial request
            return Q(pk=F("pk"))
        if isinstance(query, list):
            if query[0] == 'AND':
                return functools.reduce(operator.and_, [Permission._about(query, **kwargs) for query in query[1:]])
            elif query[0] == 'OR':
                return functools.reduce(operator.or_, [Permission._about(query, **kwargs) for query in query[1:]])
            elif query[0] == 'NOT':
                return ~Permission._about(query[1], **kwargs)
            else:
                return Q(pk=F("pk")) if Permission.compute_param(query, **kwargs) else ~Q(pk=F("pk"))
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
            raise Exception("query {} is wrong".format(query))

    def about(self, **kwargs):
        """
        Return an InstancedPermission with the parameters
        replaced by their values and the query interpreted
        """
        query = json.loads(self.query)
        # query = self._about(query, **kwargs)
        return InstancedPermission(self.model, query, self.type, self.field, self.mask, **kwargs)

    def __str__(self):
        return self.description


class Role(models.Model):
    """
    Permissions associated with a Role
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
    )

    for_club = models.ForeignKey(
        "member.Club",
        verbose_name=_("for club"),
        on_delete=models.PROTECT,
        null=True,
        default=None,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("role permissions")
        verbose_name_plural = _("role permissions")
