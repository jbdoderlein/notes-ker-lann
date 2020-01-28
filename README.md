# NoteKfet 2020

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.txt)
[![pipeline status](https://gitlab.crans.org/bde/nk20/badges/master/pipeline.svg)](https://gitlab.crans.org/bde/nk20/nk20/commits/master)
[![coverage report](https://gitlab.crans.org/bde/nk20/badges/master/coverage.svg)](https://gitlab.crans.org/bde/nk20/commits/master)

## Installation sur un serveur

On supposera pour la suite que vous utiliser debian/ubuntu sur un serveur tout nu ou bien configuré.

1. Paquets nécessaires

        $ sudo apt install nginx python3 python3-pip python3-dev uwsgi
        $ sudo apt install uwsgi-plugin-python3 python3-virtualenv git

2. Clonage du dépot

    on se met au bon endroit :

        $ cd /var/www/
        $ mkdir note_kfet
        $ cd note_kfet
        $ git clone git@gitlab.crans.org:bde/nk20.git .
3. Environment Virtuel

   À la racine du projet:

        $ virtualenv env
        $ source /env/bin/activate
        (env)$ pip install -r requirements.txt
        (env)$ deactivate

4. uwsgi  et Nginx

    On utilise uwsgi et Nginx pour gérer le coté serveu :

        $ sudo ln -s /var/www/note_kfet/nginx_note.conf /etc/nginx/sites-enabled/

   **Modifier la config nginx  pour l'adapter à votre server!**

   Si l'on a un emperor (plusieurs instance uwsgi):

        $ sudo ln -s /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/sites/

    Sinon:

        $ sudo ln -s /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/apps-enabled/
        
5. Base de données

    En prod on utilise postgresql. 
        
        $ sudo apt-get install postgresql postgresql-contrib libpq-dev
        (env)$ pip install psycopg2
    
    La config de la base de donnée se fait comme suit:
    
    a. On se connecte au shell de psql
    
        $ sudo su - postgres
        $ psql
    
    b. On sécurise l'utilisateur postgres
        
        postgres=# \password
        Enter new password:
        
     Conservez ce mot de passe de la meme manière que tous les autres.
     
    c. On créer la basse de donnée, et l'utilisateur associé
    
        postgres=# CREATE USER note WITH PASSWORD 'un_mot_de_passe_sur';
        CREATE ROLE
        postgres=# CREATE DATABASE note_db OWNER note;
        CREATE DATABASE

    Si tout va bien:
        
        postgres=#\list
        List of databases
           Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges   
        -----------+----------+----------+-------------+-------------+-----------------------
         note_db   | note     | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | 
         postgres  | postgres | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | 
         template0 | postgres | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | =c/postgres+postgres=CTc/postgres
         template1 | postgres | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | =c/postgres  +postgres=CTc/postgres
        (4 rows)
NB: cette config est en adéquation avec `note_kfet/settings/production.py`. penser à changer le mots de passe dans `note_kfet/settings/secrets.py`


6. Variable d'environnement et Migrations
        
        on modifie le fichier d'environnement:
        ```
        # env/bin/activate:
        
        deactivate () {
        ...
    
        # Unset local environment variables
        unset DJANGO_APP_STAGE
        }
        ...
        #at end of the file:
        export DJANGO_APP_STAGE="prod"
        ```
Ensuite on bascule dans l'environement virtuel et on lance les migrations
        
        $ source /env/bin/activate
        (env)$ ./manage.py makemigrations
        (env)$ ./manage.py migrate

7. Enjoy

    

## Installer en local

Il est tout a fait possible de travailler en local, vive `./manage.py runserver` !

1. Cloner le dépot là ou vous voulez:

        $ git clone git@gitlab.crans.org:bde/nk20.git

2. Initialiser l'environnement Virtuel
        
        $ cd nk20
        $ virtualenv env
        $ source /env/bin/activate
        (env)$ pip install -r requirements.txt

3. Migrations:

        (env)$ ./manage.py makemigrations
        (env)$ ./manage.py migrate

4. Enjoy:

        (env)$ ./manage.py runserver

## Minimal Setup

1. Créer un superuser :

        (env)$ ./manage.py createsuperuser

Avec ce dernier vous pouvez vous connecter à l'interface admin de Django, avoir
accès à la doc auto-générée du projet, jouer avec des models, etc ...

## Cahier des Charges 

Il est disponible [ici](https://wiki.crans.org/NoteKfet/NoteKfet2018/CdC). 

## Documentation

La documentation est générée par django et son module admindocs. **Commenter votre code !*
