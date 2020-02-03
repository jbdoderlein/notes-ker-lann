#!/bin/bash
python manage.py compilemessages
python manage.py makemigrations
sleep 5
python manage.py migrate

# TODO: use uwsgi in production
python manage.py runserver 0.0.0.0:8000
