# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ModelSerializer
from note.models import NoteUser, Alias
from note_kfet.middlewares import get_current_request

from .models import Changelog

import getpass


# Ces modèles ne nécessitent pas de logs
EXCLUDED = [
    'admin.logentry',
    'authtoken.token',
    'cas_server.proxygrantingticket',
    'cas_server.proxyticket',
    'cas_server.serviceticket',
    'cas_server.user',
    'cas_server.userattributes',
    'contenttypes.contenttype',
    'logs.changelog',  # Never remove this line
    'mailer.dontsendentry',
    'mailer.message',
    'mailer.messagelog',
    'migrations.migration',
    'note.note'  # We only store the subclasses
    'note.transaction',
    'sessions.session',
]


def pre_save_object(sender, instance, **kwargs):
    """
    Before a model get saved, we get the previous instance that is currently in the database
    """
    qs = sender.objects.filter(pk=instance.pk).all()
    if qs.exists():
        instance._previous = qs.get()
    else:
        instance._previous = None


def save_object(sender, instance, **kwargs):
    """
    Each time a model is saved, an entry in the table `Changelog` is added in the database
    in order to store each modification made
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED or hasattr(instance, "_no_signal"):
        return

    # noinspection PyProtectedMember
    previous = instance._previous

    # Si un utilisateur est connecté, on récupère l'utilisateur courant ainsi que son adresse IP
    request = get_current_request()

    if request is None:
        # Si la modification n'a pas été faite via le client Web, on suppose que c'est du à `manage.py`
        # On récupère alors l'utilisateur·trice connecté·e à la VM, et on récupère la note associée
        # IMPORTANT : l'utilisateur dans la VM doit être un des alias note du respo info
        ip = "127.0.0.1"
        username = Alias.normalize(getpass.getuser())
        note = NoteUser.objects.filter(alias__normalized_name=username)
        # if not note.exists():
        #     print("WARNING: A model attempted to be saved in the DB, but the actor is unknown: " + username)
        # else:
        if note.exists():
            user = note.get().user
        else:
            user = None
    else:
        user = request.user
        if 'HTTP_X_REAL_IP' in request.META:
            ip = request.META.get('HTTP_X_REAL_IP')
        elif 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META.get('HTTP_X_FORWARDED_FOR').split(', ')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if not user.is_authenticated:
            # For registration and OAuth2 purposes
            user = None

    # noinspection PyProtectedMember
    if request is not None and instance._meta.label_lower == "auth.user" and previous:
        # On n'enregistre pas les connexions
        if instance.last_login != previous.last_login:
            return

    changed_fields = '__all__'
    if previous:
        # On ne garde que les champs modifiés
        changed_fields = []
        for field in instance._meta.fields:
            if field.name.endswith("_ptr"):
                # A field ending with _ptr is a OneToOneRel with a subclass, e.g. NoteClub.note_ptr -> Note
                continue
            if getattr(instance, field.name) != getattr(previous, field.name):
                changed_fields.append(field.name)

    if len(changed_fields) == 0:
        # Pas de log s'il n'y a pas de modification
        return

    # On crée notre propre sérialiseur JSON pour pouvoir sauvegarder les modèles avec uniquement les champs modifiés
    class CustomSerializer(ModelSerializer):
        class Meta:
            model = instance.__class__
            fields = changed_fields

    previous_json = JSONRenderer().render(CustomSerializer(previous).data).decode("UTF-8") if previous else ""
    instance_json = JSONRenderer().render(CustomSerializer(instance).data).decode("UTF-8")

    Changelog.objects.create(user=user,
                             ip=ip,
                             model=ContentType.objects.get_for_model(instance),
                             instance_pk=instance.pk,
                             previous=previous_json,
                             data=instance_json,
                             action=("edit" if previous else "create")
                             ).save()


def delete_object(sender, instance, **kwargs):
    """
    Each time a model is deleted, an entry in the table `Changelog` is added in the database
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED or hasattr(instance, "_no_signal"):
        return

    # Si un utilisateur est connecté, on récupère l'utilisateur courant ainsi que son adresse IP
    request = get_current_request()

    if request is None:
        # Si la modification n'a pas été faite via le client Web, on suppose que c'est du à `manage.py`
        # On récupère alors l'utilisateur·trice connecté·e à la VM, et on récupère la note associée
        # IMPORTANT : l'utilisateur dans la VM doit être un des alias note du respo info
        ip = "127.0.0.1"
        username = Alias.normalize(getpass.getuser())
        note = NoteUser.objects.filter(alias__normalized_name=username)
        # if not note.exists():
        #     print("WARNING: A model attempted to be saved in the DB, but the actor is unknown: " + username)
        # else:
        if note.exists():
            user = note.get().user
        else:
            user = None
    else:
        user = request.user
        if 'HTTP_X_REAL_IP' in request.META:
            ip = request.META.get('HTTP_X_REAL_IP')
        elif 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META.get('HTTP_X_FORWARDED_FOR').split(', ')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if not user.is_authenticated:
            # For registration and OAuth2 purposes
            user = None

    # On crée notre propre sérialiseur JSON pour pouvoir sauvegarder les modèles
    class CustomSerializer(ModelSerializer):
        class Meta:
            model = instance.__class__
            fields = '__all__'

    instance_json = JSONRenderer().render(CustomSerializer(instance).data).decode("UTF-8")

    Changelog.objects.create(user=user,
                             ip=ip,
                             model=ContentType.objects.get_for_model(instance),
                             instance_pk=instance.pk,
                             previous=instance_json,
                             data="",
                             action="delete"
                             ).save()
