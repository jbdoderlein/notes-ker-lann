#!/bin/sh
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

if [ -z ${NOTE_URL+x} ]; then
  echo "Warning: your env files are not configurated."
else
  sed -i -e "s/example.com/$DOMAIN/g" /code/apps/member/fixtures/initial.json
  sed -i -e "s/localhost/$NOTE_URL/g" /code/note_kfet/fixtures/initial.json
  sed -i -e "s/\"\.\*\"/\"https?:\/\/$NOTE_URL\/.*\"/g" /code/note_kfet/fixtures/cas.json
  sed -i -e "s/REPLACEME/La Note Kfet \\\\ud83c\\\\udf7b/g" /code/note_kfet/fixtures/cas.json
fi

# Set up Django project
python3 manage.py collectstatic --noinput
python3 manage.py compilemessages
python3 manage.py makemigrations
python3 manage.py migrate

if [ "$1" ]; then
    # Command passed
    echo "Running $@..."
    $@
else
    # Launch server
    if [ "$DJANGO_APP_STAGE" = "prod" ]; then
        # FIXME: serve static files
        uwsgi --http 0.0.0.0:8080 --master --module note_kfet.wsgi --processes 4
    else
        python3 manage.py runserver 0.0.0.0:8080;
    fi
fi
