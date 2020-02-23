#!/usr/env/bin python3

from django.core.management.base import BaseCommand
from django.utils import timezone
import psycopg2 as  pg
import psycopg2.extras as pge
from django.db import transaction
import json
import collections
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from note.models import Note, NoteSpecial, NoteUser, NoteClub
from note.models import Transaction, TransactionTemplate, TransactionCategory, TransactionType
from member.models import Profile, Club


@transaction.atomic
def import_special(cur):
    cur.execute("SELECT * FROM comptes WHERE idbde <0 ORDER BY idbde;")
    map_idbde = dict()
    for row in cur:
        obj,created = NoteSpecial.objects.get_or_create(special_type = row["pseudo"],
                                                        balance = row["solde"],
                                                        is_active =True)
        if created:
            obj.save()
            map_idbde[row["idbde"]] = obj.pk

    cur.execute("SELECT * FROM comptes WHERE idbde=0;")
    res = cur.fetchone()
    clubBde, c = Club.objects.get_or_create(pk = 1,
                                            name = "Bde",
                                            email = "bureau.bde@lists.crans.org",
                                            membership_duration = "396 00:00:00",
                                            membership_start = "213 00:00:00",
                                            membership_end = "273 00:00:00",
                                            membership_fee = 5,
    )
    clubKfet, c = Club.objects.get_or_create(pk = 2,
                                             name = "Kfet",
                                             email = "tresorerie.bde@lists.crans.org",
                                             membership_duration = "396 00:00:00",
                                             membership_start = "213 00:00:00",
                                             membership_end = "273 00:00:00",
                                             membership_fee = 35,
    )
    clubBde.save()
    clubKfet.save()
    clubBde.note.solde=res["solde"]
    map_idbde[0] = clubKfet.note.pk
    return map_idbde


@transaction.atomic
def import_comptes(cur,map_idbde):
    cur.execute("SELECT * FROM comptes WHERE idbde > 0 ORDER BY idbde;")
    pkclub = 3
    for row in cur:
        if row["type"] == "personne":
            #sanitize password
            if row["passwd"] != "*|*":
                passwd_nk15 = "$".join(["custom_nk15","1",row["passwd"]])
            else:
                passwd_nk15 = ''
            try:
                user = User.objects.create(
                    username =row["pseudo"],
                    password = passwd_nk15,
                    first_name = row["nom"],
                    last_name = row["prenom"],
                    email = row["mail"],
                )
                #sanitize duplicate aliases (nk12)
            except ValidationError as e:
                if e.code == 'same_alias':
                    user = User.objects.create(
                        username = row["pseudo"]+str(row["idbde"]),
                        password = row["passwd"] if row["passwd"] != '*|*' else '',
                        first_name = row["nom"],
                        last_name = row["prenom"],
                        email = row["mail"],
                    )
                else:
                    raise(e)
            else:
                pass
            profile = Profile.objects.create(
                phone_number = row["tel"],
                address = row["adresse"],
                paid = row["normalien"],
                user = user,
            )
            note = user.note
            note.balance = row["solde"]

            obj_list =[user, profile, note]
        else:#club
            club,c = Club.objects.get_or_create(pk=pkclub,
                                                name = row["pseudo"],
                                                email = row["mail"],
                                                membership_duration = "396 00:00:00",
                                                membership_start = "213 00:00:00",
                                                membership_end = "273 00:00:00",
                                                membership_fee =0,
            )
            pkclub +=1
            note = club.note
            note.balance = row["solde"]
            obj_list = [club,note]
        for obj in obj_list:
            obj.save()
            map_idbde[row["idbde"]] = note.pk
            #
    return map_idbde

@transaction.atomic
def import_boutons(cur,map_idbde):
    cur.execute("SELECT * FROM boutons;")
    for row in cur:
        cat, created = TransactionCategory.objects.get_or_create(name=row["categorie"])

        button = TransactionTemplate.objects.create(pk=row["id"],
                                            name=row["label"],
                                            amount=row["montant"],
                                            destination_id=map_idbde[row["destinataire"]],
                                            category = cat,
                                            display = row["affiche"],
                                            description = row["description"],
        )
        if created:
            cat.save()
        button.save()


class Command(BaseCommand):
    """
    Command for importing the database of NK15.
    Need to be run by a user with a registered role in postgres for the database nk15. 
    """
    def add_arguments(self,parser):
        parser.add_argument('-s', '--special', action = 'store_true')
        parser.add_argument('-c', '--comptes', action = 'store_true')
        parser.add_argument('-b', '--boutons', action = 'store_true')


    def handle(self, *args, **kwargs):
        conn = pg.connect(database="nk15",user="nk15_user")
        cur = conn.cursor(cursor_factory = pge.DictCursor)

        if kwargs["special"]:
            map_idbde = import_special(cur)
            print("Minimal setup created")

        if kwargs["comptes"]:
            map_idbde = import_comptes(cur,map_idbde)
            print("comptes table imported")

        if kwargs["boutons"]:
            import_boutons(cur,map_idbde)
            print("boutons table imported")
        if kwargs["transaction"]:
            import_transaction(cur)
