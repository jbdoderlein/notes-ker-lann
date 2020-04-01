# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ModelSerializer
from note.models import NoteUser, Alias
from note_kfet.middlewares import get_current_authenticated_user, get_current_ip

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
    if instance._meta.label_lower in EXCLUDED:
        return

    if hasattr(instance, "_force_save"):
        return

    # noinspection PyProtectedMember
    previous = instance._previous

    # Si un utilisateur est connecté, on récupère l'utilisateur courant ainsi que son adresse IP
    user, ip = get_current_authenticated_user(), get_current_ip()

    if user is None:
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

    # noinspection PyProtectedMember
    if user is not None and instance._meta.label_lower == "auth.user" and previous:
        # On n'enregistre pas les connexions
        if instance.last_login != previous.last_login:
            return

    # On crée notre propre sérialiseur JSON pour pouvoir sauvegarder les modèles
    class CustomSerializer(ModelSerializer):
        class Meta:
            model = instance.__class__
            fields = '__all__'

    previous_json = JSONRenderer().render(CustomSerializer(previous).data).decode("UTF-8") if previous else None
    instance_json = JSONRenderer().render(CustomSerializer(instance).data).decode("UTF-8")

    if previous_json == instance_json:
        # Pas de log s'il n'y a pas de modification
        return

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
    if instance._meta.label_lower in EXCLUDED:
        return

    if hasattr(instance, "_force_delete"):
        return

    # Si un utilisateur est connecté, on récupère l'utilisateur courant ainsi que son adresse IP
    user, ip = get_current_authenticated_user(), get_current_ip()

    if user is None:
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
                             data=None,
                             action="delete"
                             ).save()
