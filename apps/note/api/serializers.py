# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from member.api.serializers import MembershipSerializer
from member.models import Membership
from note_kfet.middlewares import get_current_authenticated_user
from permission.backends import PermissionBackend
from rest_framework.utils import model_meta

from ..models.notes import Note, NoteClub, NoteSpecial, NoteUser, Alias
from ..models.transactions import TransactionTemplate, Transaction, MembershipTransaction, TemplateCategory, \
    RecurrentTransaction, SpecialTransaction


class NoteSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Notes.
    The djangorestframework plugin will analyse the model `Note` and parse all fields in the API.
    """

    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = [f.name for f in model._meta.get_fields()]  # Notes are read-only protected


class NoteClubSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Club's notes.
    The djangorestframework plugin will analyse the model `NoteClub` and parse all fields in the API.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = NoteClub
        fields = '__all__'
        read_only_fields = ('note', 'club', )

    def get_name(self, obj):
        return str(obj)


class NoteSpecialSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for special notes.
    The djangorestframework plugin will analyse the model `NoteSpecial` and parse all fields in the API.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = NoteSpecial
        fields = '__all__'
        read_only_fields = ('note', )

    def get_name(self, obj):
        return str(obj)


class NoteUserSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for User's notes.
    The djangorestframework plugin will analyse the model `NoteUser` and parse all fields in the API.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = NoteUser
        fields = '__all__'
        read_only_fields = ('note', 'user', )

    def get_name(self, obj):
        return str(obj)


class AliasSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Aliases.
    The djangorestframework plugin will analyse the model `Alias` and parse all fields in the API.
    """

    class Meta:
        model = Alias
        fields = '__all__'

    def validate(self, attrs):
        instance = Alias(**attrs)
        instance.clean()
        return attrs


class NotePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Note: NoteSerializer,
        NoteUser: NoteUserSerializer,
        NoteClub: NoteClubSerializer,
        NoteSpecial: NoteSpecialSerializer,
    }

    class Meta:
        model = Note


class ConsumerSerializer(serializers.ModelSerializer):
    """
    REST API Nested Serializer for Consumers.
    return Alias, and the note Associated to it in
    """
    note = serializers.SerializerMethodField()

    email_confirmed = serializers.SerializerMethodField()

    membership = serializers.SerializerMethodField()

    class Meta:
        model = Alias
        fields = '__all__'

    def get_note(self, obj):
        """
        Display information about the associated note
        """
        # If the user has no right to see the note, then we only display the note identifier
        if PermissionBackend.check_perm(get_current_authenticated_user(), "note.view_note", obj.note):
            return NotePolymorphicSerializer().to_representation(obj.note)
        return dict(id=obj.note.id, name=str(obj.note))

    def get_email_confirmed(self, obj):
        if isinstance(obj.note, NoteUser):
            return obj.note.user.profile.email_confirmed
        return True

    def get_membership(self, obj):
        if isinstance(obj.note, NoteUser):
            memberships = Membership.objects.filter(
                PermissionBackend.filter_queryset(get_current_authenticated_user(), Membership, "view")).filter(
                user=obj.note.user,
                club=2,  # Kfet
            ).order_by("-date_start")
            if memberships.exists():
                return MembershipSerializer().to_representation(memberships.first())
        return None


class TemplateCategorySerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transaction templates.
    The djangorestframework plugin will analyse the model `TemplateCategory` and parse all fields in the API.
    """

    class Meta:
        model = TemplateCategory
        fields = '__all__'


class TransactionTemplateSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transaction templates.
    The djangorestframework plugin will analyse the model `TransactionTemplate` and parse all fields in the API.
    """

    class Meta:
        model = TransactionTemplate
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transactions.
    The djangorestframework plugin will analyse the model `Transaction` and parse all fields in the API.
    """

    class Meta:
        model = Transaction
        fields = '__all__'


class RecurrentTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Transactions.
    The djangorestframework plugin will analyse the model `RecurrentTransaction` and parse all fields in the API.
    """

    class Meta:
        model = RecurrentTransaction
        fields = '__all__'


class MembershipTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Membership transactions.
    The djangorestframework plugin will analyse the model `MembershipTransaction` and parse all fields in the API.
    """

    class Meta:
        model = MembershipTransaction
        fields = '__all__'


class SpecialTransactionSerializer(serializers.ModelSerializer):
    """
    REST API Serializer for Special transactions.
    The djangorestframework plugin will analyse the model `SpecialTransaction` and parse all fields in the API.
    """

    class Meta:
        model = SpecialTransaction
        fields = '__all__'


# noinspection PyUnresolvedReferences
class TransactionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Transaction: TransactionSerializer,
        RecurrentTransaction: RecurrentTransactionSerializer,
        MembershipTransaction: MembershipTransactionSerializer,
        SpecialTransaction: SpecialTransactionSerializer,
    }

    try:
        from activity.models import GuestTransaction
        from activity.api.serializers import GuestTransactionSerializer
        model_serializer_mapping[GuestTransaction] = GuestTransactionSerializer
    except ImportError:  # Activity app is not loaded
        pass

    def validate(self, attrs):
        resource_type = attrs.pop(self.resource_type_field_name)
        serializer = self._get_serializer_from_resource_type(resource_type)
        if self.instance:
            instance = self.instance
            info = model_meta.get_field_info(instance)
            for attr, value in attrs.items():
                if attr in info.relations and info.relations[attr].to_many:
                    field = getattr(instance, attr)
                    field.set(value)
                else:
                    setattr(instance, attr, value)
            instance.validate(True)
        else:
            serializer.Meta.model(**attrs).validate(True)
        attrs[self.resource_type_field_name] = resource_type
        return super().validate(attrs)

    class Meta:
        model = Transaction
