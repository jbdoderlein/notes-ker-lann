#!/bin/bash
# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

python manage.py compilemessages
python manage.py makemigrations

# Wait for database
sleep 5
python manage.py migrate

# TODO: use uwsgi in production
python manage.py runserver 0.0.0.0:8000
