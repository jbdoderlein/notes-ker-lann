# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import getpass

from note.models import NoteUser, Alias
from .middlewares import get_current_authenticated_user, get_current_ip
from .models import Changelog


# Ces modèles ne nécessitent pas de logs
EXCLUDED = [
    'admin.logentry',
    'authtoken.token',
    'cas_server.user',
    'cas_server.userattributes',
    'contenttypes.contenttype',
    'logs.changelog',
    'migrations.migration',
    'note.noteuser',
    'note.noteclub',
    'note.notespecial',
    'sessions.session',
]


@receiver(pre_save)
def pre_save_object(sender, instance, **kwargs):
    """
    Avant la sauvegarde d'un modèle, on récupère l'ancienne instance actuellement en base de données
    que l'on garde en mémoire
    """
    qs = sender.objects.filter(pk=instance.pk).all()
    if qs.exists():
        instance._previous = qs.get()
    else:
        instance._previous = None


@receiver(post_save)
def save_object(sender, instance, **kwargs):
    """
    Dès qu'un modèle est sauvegardé, une entrée dans la table `Changelog` est ajouté dans la base de données
    afin de répertorier chaque modification effectuée
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
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
        note = NoteUser.objects.filter(alias__normalized_name__regex="^" + username + "$")
        if not note.exists():
            print("WARNING: A model attempted to be saved in the DB, but the actor is unknown: " + username)
        else:
            user = note.get().user

    if user is not None and instance._meta.label_lower == "auth.user" and previous:
        # On n'enregistre pas les connexions
        if instance.last_login != previous.last_login:
            return

    # Les modèles sont sauvegardés au format JSON
    previous_json = serializers.serialize('json', [previous, ])[1:-1] if previous else None
    instance_json = serializers.serialize('json', [instance, ])[1:-1]

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


@receiver(post_delete)
def delete_object(sender, instance, **kwargs):
    """
    Dès qu'un modèle est supprimé, une entrée dans la table `Changelog` est ajouté dans la base de données
    """
    # noinspection PyProtectedMember
    if instance._meta.label_lower in EXCLUDED:
        return

    # Si un utilisateur est connecté, on récupère l'utilisateur courant ainsi que son adresse IP
    user, ip = get_current_authenticated_user(), get_current_ip()

    instance_json = serializers.serialize('json', [instance, ])[1:-1]
    Changelog.objects.create(user=user,
                             ip=ip,
                             model=ContentType.objects.get_for_model(instance),
                             instance_pk=instance.pk,
                             previous=instance_json,
                             data=None,
                             action="delete"
                             ).save()
