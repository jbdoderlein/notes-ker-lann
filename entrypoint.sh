#!/bin/sh
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

if [ -z ${NOTE_URL+x} ]; then
  echo "Warning: your env files are not configurated."
else
  sed -i -e "s/example.com/$DOMAIN/g" /var/www/note_kfet/apps/member/fixtures/initial.json
  sed -i -e "s/localhost/$NOTE_URL/g" /var/www/note_kfet/note_kfet/fixtures/initial.json
  sed -i -e "s/\"\.\*\"/\"https?:\/\/$NOTE_URL\/.*\"/g" /var/www/note_kfet/note_kfet/fixtures/cas.json
  sed -i -e "s/REPLACEME/La Note Kfet \\\\ud83c\\\\udf7b/g" /var/www/note_kfet/note_kfet/fixtures/cas.json
fi

# Set up Django project
python3 manage.py collectstatic --noinput
python3 manage.py compilemessages
python3 manage.py migrate

if [ "$1" ]; then
    # Command passed
    echo "Running $@..."
    $@
else
    # Launch server
    if [ "$DJANGO_APP_STAGE" = "prod" ]; then
        uwsgi --http-socket 0.0.0.0:8080 --master --plugins python3 \
              --module note_kfet.wsgi:application --env DJANGO_SETTINGS_MODULE=note_kfet.settings \
              --processes 4 --static-map /static=/var/www/note_kfet/static --harakiri=20 --max-requests=5000 --vacuum
    else
        python3 manage.py runserver 0.0.0.0:8080;
    fi
fi
