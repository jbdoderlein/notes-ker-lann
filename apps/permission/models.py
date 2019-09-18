import json

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class InstancedPermission:

    def __init__(self, model, permission, type, field):
        self.model = model
        self.permission = permission
        self.type = type
        self.field = field

    def applies(self, obj, permission_type, field_name=None):
        if ContentType.objects.get_for_model(obj) != self.model:
            # The permission does not apply to the object
            return False
        if self.permission is None:
            if permission_type == self.type:
                if field_name is not None:
                    return field_name == self.field
                else:
                    return True
            else:
                return False
        elif isinstance(self.permission, dict):
            for field in self.permission:
                value = getattr(obj, field)
                if isinstance(value, models.Model):
                    value = value.pk
                if value != self.permission[field]:
                    return False
        elif isinstance(self.permission, type(obj.pk)):
            if obj.pk != self.permission:
                return False
        if permission_type == self.type:
            if field_name:
                return field_name == self.field
            else:
                return True
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

    permission = models.TextField()

    type = models.CharField(max_length=15, choices=PERMISSION_TYPES)

    field = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('model', 'permission', 'type', 'field')

    def clean(self):
        if self.field and self.type not in {'view', 'change'}:
            raise ValidationError(_("Specifying field applies only to view and change permission types."))

    def save(self):
        self.full_clean()
        super().save()

    def _about(_self, _permission, **kwargs):
        if _permission[0] == 'all':
            return None
        elif _permission[0] == 'pk':
            if _permission[1] in kwargs:
                return kwargs[_permission[1]].pk
            else:
                return None
        elif _permission[0] == 'filter':
            return {field: _self._about(_permission[1][field], **kwargs) for field in _permission[1]}
        else:
            return _permission

    def about(self, **kwargs):
        permission = json.loads(self.permission)
        permission = self._about(permission, **kwargs)
        return InstancedPermission(self.model, permission, self.type, self.field)

    def __str__(self):
        if self.field:
            return _("Can {type} {model}.{field} in {permission}").format(type=self.type, model=self.model, field=self.field, permission=self.permission)
        else:
            return _("Can {type} {model} in {permission}").format(type=self.type, model=self.model, permission=self.permission)


class UserPermission(models.Model):

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

