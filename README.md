# NoteKfet 2020

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.txt)
[![pipeline status](https://gitlab.crans.org/bde/nk20/badges/master/pipeline.svg)](https://gitlab.crans.org/bde/nk20/commits/master)
[![coverage report](https://gitlab.crans.org/bde/nk20/badges/master/coverage.svg)](https://gitlab.crans.org/bde/nk20/commits/master)

## Installation sur un serveur

On supposera pour la suite que vous utilisez une installation de Debian Buster ou Ubuntu 20.04 fraîche ou bien configuré.

Pour aller vite vous pouvez lancer le Playbook Ansible fournit dans ce dépôt en l'adaptant.
Sinon vous pouvez suivre les étapes ici.

### Installation avec Debian/Ubuntu

1.  **Installation des dépendances APT.**

    ```bash
    $ sudo apt install nginx python3 python3-pip python3-dev uwsgi uwsgi-plugin-python3 python3-venv git acl
    ```

    La génération des factures de l'application trésorerie nécessite une installation de LaTeX suffisante,

    ```bash
    $ sudo apt install texlive-latex-extra texlive-fonts-extra texlive-lang-french
    ```

2.  **Clonage du dépot** dans `/var/www/note_kfet`,

    ```bash
    $ mkdir -p /var/www/note_kfet && cd /var/www/note_kfet
    $ sudo chown www-data:www-data .
    $ sudo chmod g+rwx .
    $ sudo -u www-data git clone git@gitlab.crans.org:bde/nk20.git .
    ```

3.  **Création d'un environment de travail Python décorrélé du système.**

    ```bash
    $ python3 -m venv env
    $ source env/bin/activate
    (env)$ pip3 install -r requirements/base.txt
    (env)$ pip3 install -r requirements/prod.txt  # uniquement en prod, nécessite une base postgres
    (env)$ deactivate  # sortir de l'environnement
    ```

4.  **Pour configurer UWSGI et NGINX**, des exemples de conf sont disponibles.
    **_Modifier le fichier pour être en accord avec le reste de votre config_**

    ```bash
    $ cp nginx_note.conf_example nginx_note.conf
    $ sudo ln -sf /var/www/note_kfet/nginx_note.conf /etc/nginx/sites-enabled/
    ```

    Si l'on a un emperor (plusieurs instance uwsgi):

    ```bash
    $ sudo ln -sf /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/sites/
    ```

    Sinon si on est dans le cas habituel :

    ```bash
    $ sudo ln -sf /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/apps-enabled/
    ```
  
    Le touch-reload est activé par défault, pour redémarrer la note il suffit donc de faire `touch uwsgi_note.ini`.

5.  **Base de données.** En production on utilise PostgreSQL. 

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

    Si tout va bien :

        postgres=#\list
        List of databases
           Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges   
        -----------+----------+----------+-------------+-------------+-----------------------
         note_db   | note     | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | 
         postgres  | postgres | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | 
         template0 | postgres | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | =c/postgres+postgres=CTc/postgres
         template1 | postgres | UTF8     | fr_FR.UTF-8 | fr_FR.UTF-8 | =c/postgres  +postgres=CTc/postgres
        (4 rows)

6.  Variable d'environnement et Migrations

    On copie le fichier `.env_example` vers le fichier `.env` à la racine du projet 
    et on renseigne des secrets et des paramètres :

        DJANGO_APP_STAGE=dev # ou "prod" 
        DJANGO_DEV_STORE_METHOD=sqlite # ou "postgres"
        DJANGO_DB_HOST=localhost
        DJANGO_DB_NAME=note_db
        DJANGO_DB_USER=note
        DJANGO_DB_PASSWORD=CHANGE_ME
        DJANGO_DB_PORT=
        DJANGO_SECRET_KEY=CHANGE_ME
        DJANGO_SETTINGS_MODULE="note_kfet.settings
        NOTE_URL=localhost # URL où accéder à la note
        DOMAIN=localhost # note.example.com
        CONTACT_EMAIL=tresorerie.bde@localhost
        # Le reste n'est utile qu'en production, pour configurer l'envoi des mails
        NOTE_MAIL=notekfet@localhost
        EMAIL_HOST=smtp.localhost
        EMAIL_PORT=25
        EMAIL_USER=notekfet@localhost
        EMAIL_PASSWORD=CHANGE_ME
        WIKI_USER=NoteKfet2020
        WIKI_PASSWORD=CHANGE_ME


    Ensuite on (re)bascule dans l'environement virtuel et on lance les migrations

        $ source /env/bin/activate
        (env)$ ./manage.py check # pas de bêtise qui traine
        (env)$ ./manage.py makemigrations
        (env)$ ./manage.py migrate

7.  *Enjoy \o/*

### Installation avec Docker

Il est possible de travailler sur une instance Docker.

Pour construire l'image Docker `nk20`,

```
git clone https://gitlab.crans.org/bde/nk20/ && cd nk20
docker build . -t nk20
```

Ensuite pour lancer la note Kfet en tant que vous (option `-u`),
l'exposer sur son port 80 (option `-p`) et monter le code en écriture (option `-v`),

```
docker run -it --rm -u $(id -u):$(id -g) -v "$(pwd):/var/www/note_kfet/" -p 80:8080 nk20
```

Si vous souhaitez lancer une commande spéciale, vous pouvez l'ajouter à la fin, par exemple,

```
docker run -it --rm -u $(id -u):$(id -g) -v "$(pwd):/var/www/note_kfet/" -p 80:8080 nk20 python3 ./manage.py createsuperuser
```

#### Avec Docker Compose

On vous conseilles de faire un fichier d'environnement `.env` en prenant exemple sur `.env_example`.

Pour par exemple utiliser le Docker de la note Kfet avec Traefik pour réaliser le HTTPS,

```YAML
nk20:
  build: /chemin/vers/le/code/nk20
  volumes:
    - /chemin/vers/le/code/nk20:/var/www/note_kfet/
  env_file: /chemin/vers/le/code/nk20/.env
  restart: always
  labels:
    - traefik.domain=ndd.example.com
    - traefik.frontend.rule=Host:ndd.example.com
    - traefik.port=8080
```

### Lancer un serveur de développement

Avec `./manage.py runserver` il est très rapide de mettre en place
un serveur de développement par exemple sur son ordinateur.

1.  Cloner le dépôt là où vous voulez :

        $ git clone git@gitlab.crans.org:bde/nk20.git && cd nk20

2.  Créer un environnement Python isolé
    pour ne pas interférer avec les versions de paquets systèmes :

         $ python3 -m venv venv
         $ source venv/bin/activate
         (env)$ pip install -r requirements/base.txt

3.  Copier le fichier `.env_example` vers `.env` à la racine du projet et mettre à jour
    ce qu'il faut

4.  Migrations et chargement des données initiales :

        (env)$ ./manage.py makemigrations
        (env)$ ./manage.py migrate
        (env)$ ./manage.py loaddata initial

5.  Créer un super-utilisateur :

        (env)$ ./manage.py createsuperuser

6.  Enjoy :

        (env)$ ./manage.py runserver 0.0.0.0:8000

En mettant `0.0.0.0:8000` après `runserver`, vous rendez votre instance Django
accessible depuis l'ensemble de votre réseau, pratique pour tester le rendu
de la note sur un téléphone !

## Documentation

Le cahier des charges initial est disponible [sur le Wiki Crans](https://wiki.crans.org/NoteKfet/NoteKfet2018/CdC).

La documentation des classes et fonctions est directement dans le code et est explorable à partir de la partie documentation de l'interface d'administration de Django.
**Commentez votre code !**

La documentation plus haut niveau sur le développement est disponible sur [le Wiki associé au dépôt Git](https://gitlab.crans.org/bde/nk20/-/wikis/home).

## FAQ

### Regénérer les fichiers de traduction

Pour regénérer les traductions vous pouvez vous placer à la racine du projet et lancer le script `makemessages`. Il faut penser à ignorer les dossiers ne contenant pas notre code, dont le virtualenv.

```bash
django-admin makemessages -i env
```

Une fois les fichiers édités, vous pouvez compiler les nouvelles traductions avec

```bash
django-admin compilemessages
```
