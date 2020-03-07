from django.contribs.contenttype.models import ContentType
from member.models import Club, Membership, RolePermissions


class PermissionBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username, password):
        return None

    def permissions(self, user, obj):
        for membership in user.memberships.all():
            if not membership.valid() or membership.role is None:
                continue
            for permission in RolePermissions.objects.get(role=membership.role).permissions.objects.all():
                permission = permission.about(user=user, club=membership.club)
                yield permission

    def has_perm(self, user_obj, perm, obj=None):
        if obj is None:
            return False
        perm = perm.split('_', 3)
        perm_type = perm[1]
        perm_field = perm[2] if len(perm) == 3 else None
        return any(permission.applies(obj, perm_type, perm_field) for obj in self.permissions(user_obj, obj))

    def get_all_permissions(self, user_obj, obj=None):
        if obj is None:
            return []
        else:
            return list(self.permissions(user_obj, obj))
