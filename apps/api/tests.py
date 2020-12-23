# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from datetime import datetime, date
from urllib.parse import quote_plus
from warnings import warn

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from member.models import Membership, Club
from note.models import NoteClub, NoteUser, Alias, Note
from permission.models import PermissionMask, Permission, Role
from phonenumbers import PhoneNumber
from rest_framework.filters import SearchFilter

from .viewsets import ContentTypeViewSet, UserViewSet


class TestAPI(TestCase):
    """
    Load API pages and check that filters are working.
    """
    fixtures = ('initial', )

    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            username="adminapi",
            password="adminapi",
            email="adminapi@example.com",
            last_name="Admin",
            first_name="Admin",
        )
        self.client.force_login(self.user)

        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

    def check_viewset(self, viewset, url):
        """
        This function should be called inside a unit test.
        This loads the viewset and for each filter entry, it checks that the filter is running good.
        """
        resp = self.client.get(url + "?format=json")
        self.assertEqual(resp.status_code, 200)

        model = viewset.serializer_class.Meta.model

        if not model.objects.exists():  # pragma: no cover
            warn(f"Warning: unable to test API filters for the model {model._meta.verbose_name} "
                 "since there is no instance of it.")
            return

        if hasattr(viewset, "filter_backends"):
            backends = viewset.filter_backends
            obj = model.objects.last()

            if DjangoFilterBackend in backends:
                # Specific search
                for field in viewset.filterset_fields:
                    obj = self.fix_note_object(obj, field)

                    value = self.get_value(obj, field)
                    if value is None:  # pragma: no cover
                        warn(f"Warning: the filter {field} for the model {model._meta.verbose_name} "
                             "has not been tested.")
                        continue
                    resp = self.client.get(url + f"?format=json&{field}={quote_plus(str(value))}")
                    self.assertEqual(resp.status_code, 200, f"The filter {field} for the model "
                                                            f"{model._meta.verbose_name} does not work. "
                                                            f"Given parameter: {value}")
                    content = json.loads(resp.content)
                    self.assertGreater(content["count"], 0, f"The filter {field} for the model "
                                                            f"{model._meta.verbose_name} does not work. "
                                                            f"Given parameter: {value}")

            if OrderingFilter in backends:
                # Ensure that ordering is working well
                for field in viewset.ordering_fields:
                    resp = self.client.get(url + f"?ordering={field}")
                    self.assertEqual(resp.status_code, 200)
                    resp = self.client.get(url + f"?ordering=-{field}")
                    self.assertEqual(resp.status_code, 200)

            if SearchFilter in backends:
                # Basic search
                for field in viewset.search_fields:
                    obj = self.fix_note_object(obj, field)

                    if field[0] == '$' or field[0] == '=':
                        field = field[1:]
                    value = self.get_value(obj, field)
                    if value is None:  # pragma: no cover
                        warn(f"Warning: the filter {field} for the model {model._meta.verbose_name} "
                             "has not been tested.")
                        continue
                    resp = self.client.get(url + f"?format=json&search={quote_plus(str(value))}")
                    self.assertEqual(resp.status_code, 200, f"The filter {field} for the model "
                                                            f"{model._meta.verbose_name} does not work. "
                                                            f"Given parameter: {value}")
                    content = json.loads(resp.content)
                    self.assertGreater(content["count"], 0, f"The filter {field} for the model "
                                                            f"{model._meta.verbose_name} does not work. "
                                                            f"Given parameter: {value}")

            self.check_permissions(url, obj)

    def check_permissions(self, url, obj):
        """
        Check that permissions are working
        """
        # Drop rights
        self.user.is_superuser = False
        self.user.save()
        sess = self.client.session
        sess["permission_mask"] = 0
        sess.save()

        # Delete user permissions
        for m in Membership.objects.filter(user=self.user).all():
            m.roles.clear()
            m.save()

        # Create a new role, which will have the checking permission
        role = Role.objects.get_or_create(name="β-tester")[0]
        role.permissions.clear()
        role.save()
        membership = Membership.objects.get_or_create(user=self.user, club=Club.objects.get(name="BDE"))[0]
        membership.roles.set([role])
        membership.save()

        # Ensure that the access to the object is forbidden without permission
        resp = self.client.get(url + f"{obj.pk}/")
        self.assertEqual(resp.status_code, 404, f"Mysterious access to {url}{obj.pk}/ for {obj}")

        obj.refresh_from_db()

        # There are problems with polymorphism
        if isinstance(obj, Note) and hasattr(obj, "note_ptr"):
            obj = obj.note_ptr

        mask = PermissionMask.objects.get(rank=0)

        for field in obj._meta.fields:
            # Build permission query
            value = self.get_value(obj, field.name)
            if isinstance(value, date) or isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, ImageFieldFile):
                value = value.name
            query = json.dumps({field.name: value})

            # Create sample permission
            permission = Permission.objects.get_or_create(
                model=ContentType.objects.get_for_model(obj._meta.model),
                query=query,
                mask=mask,
                type="view",
                permanent=False,
                description=f"Can view {obj._meta.verbose_name}",
            )[0]
            role.permissions.set([permission])
            role.save()

            # Check that the access is possible
            resp = self.client.get(url + f"{obj.pk}/")
            self.assertEqual(resp.status_code, 200, f"Permission {permission.query} is not working "
                                                    f"for the model {obj._meta.verbose_name}")

        # Restore rights
        self.user.is_superuser = True
        self.user.save()
        sess = self.client.session
        sess["permission_mask"] = 42
        sess.save()

    @staticmethod
    def get_value(obj, key: str):
        """
        Resolve the queryset filter to get the Python value of an object.
        """
        if hasattr(obj, "all"):
            # obj is a RelatedManager
            obj = obj.last()

        if obj is None:  # pragma: no cover
            return None

        if '__' not in key:
            obj = getattr(obj, key)
            if hasattr(obj, "pk"):
                return obj.pk
            elif hasattr(obj, "all"):
                if not obj.exists():  # pragma: no cover
                    return None
                return obj.last().pk
            elif isinstance(obj, bool):
                return int(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, PhoneNumber):
                return obj.raw_input
            return obj

        key, remaining = key.split('__', 1)
        return TestAPI.get_value(getattr(obj, key), remaining)

    @staticmethod
    def fix_note_object(obj, field):
        """
        When querying an object that has a noteclub or a noteuser field,
        ensure that the object has a good value.
        """
        if isinstance(obj, Alias):
            if "noteuser" in field:
                return NoteUser.objects.last().alias.last()
            elif "noteclub" in field:
                return NoteClub.objects.last().alias.last()
        elif isinstance(obj, Note):
            if "noteuser" in field:
                return NoteUser.objects.last()
            elif "noteclub" in field:
                return NoteClub.objects.last()
        return obj


class TestBasicAPI(TestAPI):
    def test_user_api(self):
        """
        Load the user page.
        """
        self.check_viewset(ContentTypeViewSet, "/api/models/")
        self.check_viewset(UserViewSet, "/api/user/")
