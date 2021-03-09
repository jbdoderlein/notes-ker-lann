# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from rest_framework.generics import RetrieveAPIView

from .serializers import OAuthSerializer


class UserInformationView(RetrieveAPIView):
    """
    These fields are give to OAuth authenticators.
    """
    serializer_class = OAuthSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        return self.request.user
