# NoteKfet 2020

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.txt)
[![pipeline status](https://gitlab.crans.org/bde/nk20/badges/master/pipeline.svg)](https://gitlab.crans.org/bde/nk20/nk20/commits/master)
[![coverage report](https://gitlab.crans.org/bde/nk20/badges/master/coverage.svg)](https://gitlab.crans.org/bde/nk20/commits/master)

## Installation sur un serveur

On supposera pour la suite que vous utiliser debian/ubuntu sur un serveur tout nu ou bien configuré.

1. Paquets nécessaires

        $ sudo apt install nginx python3 python3-pip python3-dev uwsgi
        $ sudo apt install uwsgi-plugin-python3 python3-venv git acl

2. Clonage du dépot

    on se met au bon endroit :

        $ cd /var/www/
        $ mkdir note_kfet
        $ sudo chown www-data:www-data note_kfet
        $ sudo usermod -a -G www-data $USER
        $ sudo chmod g+ws note_kfet
        $ sudo setfacl -d -m "g::rwx" note_kfet
        $ cd note_kfet
        $ git clone git@gitlab.crans.org:bde/nk20.git .
3. Environment Virtuel

   À la racine du projet:

        $ python3 -m venv env
        $ source env/bin/activate
        (env)$ pip3 install -r requirements.txt
        (env)$ deactivate

4. uwsgi  et Nginx

    Un exemple de conf est disponible :

        $ cp nginx_note.conf_example nginx_note.conf

***Modifier le fichier pour être en accord avec le reste de votre config***

    On utilise uwsgi et Nginx pour gérer le coté serveur :

        $ sudo ln -sf /var/www/note_kfet/nginx_note.conf /etc/nginx/sites-enabled/


    Si l'on a un emperor (plusieurs instance uwsgi):

        $ sudo ln -sf /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/sites/

    Sinon:

        $ sudo ln -sf /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/apps-enabled/
        
    Le touch-reload est activé par défault, pour redémarrer la note il suffit donc de faire `touch uwsgi_note.ini`.

5. Base de données

    En prod on utilise postgresql. 
        
        $ sudo apt-get install postgresql postgresql-contrib libpq-dev
        (env)$ pip3 install psycopg2
    
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

    Dans un fichier `.env` à la racine du projet on renseigne des secrets:
    
        DJANGO_APP_STAGE='prod'
        DJANGO_DB_PASSWORD='le_mot_de_passe_de_la_bdd'
        DJANGO_SECRET_KEY='une_secret_key_longue_et_compliquee'
        ALLOWED_HOSTS='le_ndd_de_votre_instance'
    

6. Variable d'environnement et Migrations
        

Ensuite on (re)bascule dans l'environement virtuel et on lance les migrations

        $ source /env/bin/activate
        (env)$ ./manage.py check # pas de bétise qui traine
        (env)$ ./manage.py makemigrations
        (env)$ ./manage.py migrate

7. Enjoy


## Installer avec Docker

Il est possible de travailler sur une instance Docker.

1. Cloner le dépôt là où vous voulez :
    
        $ git clone git@gitlab.crans.org:bde/nk20.git

2. Dans le fichier `docker_compose.yml`, qu'on suppose déjà configuré,
   ajouter les lignes suivantes, en les adaptant à la configuration voulue :

        nk20:
          build: /chemin/vers/nk20
          volumes:
            - /chemin/vers/nk20:/code/
          restart: always
          labels:
            - traefik.domain=ndd.exemple.com
            - traefik.frontend.rule=Host:ndd.exemple.com
            - traefik.port=8000

3. Enjoy :

        $ docker-compose up -d nk20

## Installer un serveur de développement

Avec `./manage.py runserver` il est très rapide de mettre en place
un serveur de développement par exemple sur son ordinateur.

1. Cloner le dépôt là où vous voulez :

        $ git clone git@gitlab.crans.org:bde/nk20.git && cd nk20

2. Créer un environnement Python isolé
   pour ne pas interférer avec les versions de paquets systèmes :

        $ python3 -m venv venv
        $ source venv/bin/activate
        (env)$ pip install -r requirements.txt

3. Migrations et chargement des données initiales :

        (env)$ ./manage.py makemigrations
        (env)$ ./manage.py migrate
        (env)$ ./manage.py loaddata initial

4. Créer un super-utilisateur :

        (env)$ ./manage.py createsuperuser

5. Enjoy :

        (env)$ ./manage.py runserver 0.0.0.0:8000

En mettant `0.0.0.0:8000` après `runserver`, vous rendez votre instance Django
accessible depuis l'ensemble de votre réseau, pratique pour tester le rendu
de la note sur un téléphone !

## Cahier des Charges 

Il est disponible [ici](https://wiki.crans.org/NoteKfet/NoteKfet2018/CdC). 

## Documentation

La documentation est générée par django et son module admindocs.
**Commenter votre code !**
