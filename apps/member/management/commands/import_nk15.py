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
from member.models import Profile, Club

class Command(BaseCommand):
    """
    Command for importing the database of NK15.
    Need to be run by a user with a registered role in postgres for the database nk15. 
    """

    def handle(self, *args, **options):
        conn = pg.connect(database="nk15",user="nk15_user")
        cur = conn.cursor(cursor_factory = pge.DictCursor)

        #  Start with Special accounts
        cur.execute("SELECT * FROM comptes WHERE idbde <0 ORDER BY idbde;")

        for row in cur:
            with transaction.atomic():
                obj,created = NoteSpecial.objects.get_or_create(special_type = row["pseudo"],
                                   balance = row["solde"],
                                   is_active =True)
                if created:
                    obj.save()
                    # The rest
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

        cur.execute("SELECT * FROM comptes WHERE idbde > 0 ORDER BY idbde;")
        pkclub = 3
        with transaction.atomic():
            for row in cur:
                row["idbde"] += 7 # do not overwrite the already populated id.
                if row["type"] == "personne":
                    try:
                        user = User.objects.create(
                            username =row["pseudo"],
                            password = row["passwd"] if row["passwd"] != '*|*' else '',
                            first_name = row["nom"],
                            last_name = row["prenom"],
                            email = row["mail"],
                        )
                    except ValidationError as e:
                        if e.code == 'same_alias':
                            user = User.objects.create(
                                username = row["pseudo"]+str(row["idbde"]),
                                password = row["passwd"] if row["passwd"] != '*|*' else '',
                                first_name = row["nom"],
                                last_name = row["prenom"],
                                email = row["mail"],
                            )


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
                    print(row)
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
                    #endfor
