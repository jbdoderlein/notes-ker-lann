#!/usr/env/bin python3

from django.core.management.base import BaseCommand
from django.utils import timezone
import psycopg2 as  pg
import json


class Command(BaseCommand):
    """
    Command for importing the database of NK15.
    Need to be run by a user with a registered role in postgres for the database nk15. 
    """
    help = 'Displays current time'

    def add_arguments(self,parser):
        parser.add_argument("--map",type=str,help="json mapping of table header to field models")


    def handle(self, *args, **options):
        map_file= options.get("map",None)
        with open(map_file,'rb') as f:
            map_dict = json.load(f);
        
       #conn = pg.connect(database="nk15",user="nk_15")
       #cur = conn.cursor()

        for old_table in map_dict:
            print(old_table)

