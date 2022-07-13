# Notes Ker Lann (NKL)

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.txt)
[![pipeline status](https://gitlab.crans.org/bde/nk20/badges/main/pipeline.svg)](https://gitlab.crans.org/bde/nk20/commits/main)
[![coverage report](https://gitlab.crans.org/bde/nk20/badges/main/coverage.svg)](https://gitlab.crans.org/bde/nk20/commits/main)

Fork de [nk20](https://gitlab.crans.org/bde/nk20) le 13/07/2022.

## Table des matières

  - [Installation d'une instance de développement](#installation-dune-instance-de-développement)
  - [Installation d'une instance de production](#installation-dune-instance-de-production)

## Installation d'une instance de développement

L'instance de développement installe la majorité des dépendances dans un environnement Python isolé.
Bien que cela permette de créer une instance sur toutes les distributions,
**cela veut dire que vos dépendances ne seront pas mises à jour automatiquement.**

1.  **Installation des dépendances de la distribution.**
    Il y a quelques dépendances qui ne sont pas trouvable dans PyPI.
    On donne ci-dessous l'exemple pour une distribution basée sur Debian, mais vous pouvez facilement adapter pour ArchLinux ou autre.

    ```bash
    $ sudo apt update
    $ sudo apt install --no-install-recommends -y \
        ipython3 python3-setuptools python3-venv python3-dev \
        texlive-xetex gettext libjs-bootstrap4 fonts-font-awesome git
    ```

2.  **Clonage du dépot** là où vous voulez :

    ```bash
    $ git clone git@gitlab.crans.org:bde/nk20.git --recursive && cd nk20
    ```

3.  **Création d'un environment de travail Python décorrélé du système.**
    On n'utilise pas `--system-site-packages` ici pour ne pas avoir des clashs de versions de modules avec le système.

    ```bash
    $ python3 -m venv env
    $ source env/bin/activate  # entrer dans l'environnement
    (env)$ pip3 install -r requirements.txt
    (env)$ deactivate  # sortir de l'environnement
    ```

4.  **Variable d'environnement.**
    Copier le fichier `.env_example` vers `.env` à la racine du projet et mettre à jour
    ce qu'il faut.

5.  **Migrations et chargement des données initiales.**
    Pour initialiser la base de données avec de quoi travailler.

    ```bash
    (env)$ ./manage.py collectstatic --noinput
    (env)$ ./manage.py compilemessages
    (env)$ ./manage.py makemigrations
    (env)$ ./manage.py migrate
    (env)$ ./manage.py loaddata initial
    (env)$ ./manage.py createsuperuser  # Création d'un utilisateur initial
    ```

6.  Enjoy :

    ```bash
    (env)$ ./manage.py runserver 0.0.0.0:8000
    ```

En mettant `0.0.0.0:8000` après `runserver`, vous rendez votre instance Django
accessible depuis l'ensemble de votre réseau, pratique pour tester le rendu
de la note sur un téléphone !

## Installation d'une instance de production
Pour déployer facilement la note il est possible d'utiliser le playbook Ansible (sinon vous pouvez toujours le faire a la main, voir plus bas).
### Avec ansible
Il vous faudra un serveur sous debian ou ubuntu connecté à internet et que vous souhaiterez accéder à cette instance de la note sur `note.nomdedomaine.tld`.

0. Installer Ansible sur votre machine personnelle.

0. (bis) cloner le dépot sur votre machine personelle.

1.  Copier le fichier `ansible/host_example`
``` bash
$ cp ansible/hosts_example ansible/hosts
```
et ajouter sous [dev] et/ou [prod] les serveurs sur lesquels vous souhaitez installer la note.
2.  Créer un fichier `ansible/host_vars/<note.nomdedomaine.tld.yaml>` sur le modèle des fichiers existants dans `ansible/hosts` et compléter les variables nécessaires.

3. lancer `ansible/base.yaml -l <nomdedomaine.tld.yaml>`
4. Aller vous faire un café, ca peux durer un moment.

### Installation manuelle

**En production on souhaite absolument utiliser les modules Python packagées dans le gestionnaire de paquet.**
Cela permet de mettre à jour facilement les dépendances critiques telles que Django.

L'installation d'une instance de production néccessite **une installation de Debian Buster ou d'Ubuntu 20.04**.

Sinon vous pouvez suivre les étapes décrites ci-dessous.

0.  Sous Debian Buster, **activer Debian Backports.** En effet Django 2.2 LTS n'est que disponible dans les backports.

    ```bash
    $ echo "deb http://deb.debian.org/debian buster-backports main" | sudo tee /etc/apt/sources.list.d/deb_debian_org_debian.list
    ```

1.  **Installation des dépendances APT.**
    On tire les dépendances le plus possible à partir des dépôts de Debian.
    On a besoin d'un environnement LaTeX pour générer les factures.

    ```bash
    $ sudo apt update
    $ sudo apt install --no-install-recommends -t buster-backports -y \
        python3-django python3-django-crispy-forms \
        python3-django-extensions python3-django-filters python3-django-polymorphic \
        python3-djangorestframework python3-django-oauth-toolkit python3-psycopg2 python3-pil \
        python3-babel python3-lockfile python3-pip python3-phonenumbers python3-memcache ipython3 \
        python3-bs4 python3-setuptools python3-docutils \
        memcached uwsgi uwsgi-plugin-python3 \
        texlive-xetex gettext libjs-bootstrap4 fonts-font-awesome \
        nginx python3-venv git acl
    ```

2.  **Clonage du dépot** dans `/var/www/note_kfet`,

    ```bash
    $ sudo mkdir -p /var/www/note_kfet && cd /var/www/note_kfet
    $ sudo chown www-data:www-data .
    $ sudo chmod g+rwx .
    $ sudo -u www-data git clone https://gitlab.crans.org/bde/nk20.git --recursive
    ```

3.  **Création d'un environment de travail Python décorrélé du système.**

    ```bash
    $ python3 -m venv env --system-site-packages
    $ source env/bin/activate  # entrer dans l'environnement
    (env)$ pip3 install -r requirements.txt
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

        $ sudo apt-get install postgresql postgresql-contrib

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
        (env)$ ./manage.py migrate

7.  *Enjoy \o/*

### Installation avec Docker

Il est possible de travailler sur une instance Docker.

Pour construire l'image Docker `nk20`,

```
git clone https://gitlab.crans.org/bde/nk20/ --recursive && cd nk20
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
    - "traefik.http.routers.nk20.rule=Host(`ndd.example.com`)"
    - "traefik.http.services.nk20.loadbalancer.server.port=8080"
```

## Documentation

Le cahier des charges initial est disponible [sur le Wiki Crans](https://wiki.crans.org/NoteKfet/NoteKfet2018/CdC).

La documentation des classes et fonctions est directement dans le code et est explorable à partir de la partie documentation de l'interface d'administration de Django.
**Commentez votre code !**

La documentation plus haut niveau sur le développement et sur l'utilisation
est disponible sur <https://note.crans.org/doc> et également dans le dossier `docs`.

## FAQ

### Regénérer les fichiers de traduction

Pour regénérer les traductions vous pouvez vous placer à la racine du projet et lancer le script `makemessages`.
Il faut penser à ignorer les dossiers ne contenant pas notre code, dont le virtualenv.
De plus, il faut aussi extraire les variables des fichiers JavaScript.

```bash
python3 manage.py makemessages -i env
python3 manage.py makemessages -i env -e js -d djangojs
```

Une fois les fichiers édités, vous pouvez compiler les nouvelles traductions avec

```bash
python3 manage.py compilemessages
python3 manage.py compilejsmessages
```
