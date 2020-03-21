#!/bin/bash
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

python manage.py compilemessages
python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:8000
