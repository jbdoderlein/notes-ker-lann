Installer la Note Kfet en production
====================================

Cette page détaille comment installer la Note Kfet sur un serveur de production,
dédié uniquement à l'utilisation de la note. On supposera que le serveur tourne
avec un Debian Buster à jour.


Ajout des dépôts buster-backports
---------------------------------

Debian c'est bien, c'est stable, mais les paquets sont vite obsolètes.
En particulier, la version stable de Django dans la version stable de Debian est la
version 1.11, qui n'est plus maintenue par Django depuis déjà quelques mois.
Les versions stables de Django sont les versions 2.2 et 3.2, Debian Bullseye
utilisant la version 2.2.

Afin de permettre à ses utilisateurs d'utiliser les dernières fonctionnalités de
certains paquets, Debian a créé une distribution particulière, appelée
``buster-backports``. Cette distribution contient des paquets de la distribution
à venir « ``testing`` » (``bullseye`` à l'heure où cette documentation est écrite)
recompilés et réadapter pour fonctionner avec les paquets de la distribution stable
(``buster``). Ce qui nous intéresse est de pouvoir récupérer Django 2.2 depuis
cette distribution, et avoir donc une version maintenue de Django.

Plus de détails sur le wiki de Debian : `<https://wiki.debian.org/fr/Backports>`_.

Pour activer les backports, il suffit d'ajouter dans le fichier ``/etc/apt/sources.list`` :

.. code::

   deb     $MIRROR/debian buster-backports main contrib

où ``$MIRROR`` est votre miroir Debian favori, comme ``http://ftp.debian.org`` ou
``http://mirror.crans.org`` pour ce qui est de la version utilisée en production au BDE
sur les serveurs du Crans. Il suffit ensuite de faire un ``sudo apt update``.
Vérifiez que les paquets sont bien récupérés, en cherchant cette ligne :

.. code::

   Get:4 http://mirror.crans.org/debian buster-backports InRelease [46.7 kB]

.. warning::

   Avis aux futurs respos info : pensez à bien actualiser cette documentation lorsque
   Debian Bullseye sera sorti. En particulier, il ne sera pas déconnant de continuer
   à utiliser non pas buster-backports mais bullseye-backports pour installer la
   note avec Django 3.2 et non Django 2.2.

   Bien sûr, vous testerez sur un serveur qui n'est pas celui utilisé avant :)


Installation des dépendances nécessaires
----------------------------------------

On s'efforce pour récupérer le plus possible de dépendances via les paquets Debian
plutôt que via ``pip`` afin de faciliter les mises à jour et avoir une installation
plus propre. On peut donc installer tout ce dont on a besoin, depuis buster-backports :

.. code:: bash

   $ sudo apt update
   $ sudo apt install -t buster-backports --no-install-recommends \
       gettext git ipython3 \  # Dépendances basiques
       fonts-font-awesome libjs-bootstrap4 \  # Pour l'affichage web
       python3-bs4 python3-django python3-django-crispy-forms python3-django-extensions \
       python3-django-filters python3-django-oauth-toolkit python3-django-polymorphic \
       python3-djangorestframework python3-memcache python3-phonenumbers \
       python3-pil python3-pip python3-psycopg2 python3-setuptools python3-venv \
       texlive-xetex memcached

Ces paquets fournissent une bonne base sur laquelle travailler.

Pour les mettre à jour, il suffit de faire ``sudo apt update`` puis ``sudo apt upgrade``.


Téléchargement de la note
-------------------------

Tout comme en développement, on utilise directement le Gitlab du Crans pour récupérer
les sources.

On suppose que l'on veut cloner le projet dans le dossier ``/var/www/note_kfet``.

On clone donc le dépôt en tant que ``www-data`` :

.. code:: bash

   $ sudo -u www-data git clone https://gitlab.crans.org/bde/nk20.git /var/www/note_kfet

Par défaut, le dépôt est configuré pour suivre la branche ``master``, qui est la branche
stable, notamment installée sur `<https://note.crans.org/>`_. Pour changer de branche,
notamment passer sur la branche ``beta`` sur un serveur de pré-production (un peu comme
`<https://note-dev.crans.org/>`_), on peut faire :

.. code:: bash

   $ sudo -u www-data git checkout beta

.. warning::
   Avis aux successeurs : notamment pour le serveur de production derrière
   `<https://note.crans.org>`_, il peut être intéressant de créer un paquet Python
   de sorte à pouvoir installer la note en faisant directement
   ``pip install git+https://gitlab.crans.org/bde/nk20.git``, et avoir ainsi une
   installation plus propre en décourageant le développement en production.

   Voir par exemple comment le futur site d'inscription du Crans, Constellation,
   gère cela : `<https://gitlab.crans.org/nounous/constellation>`_.


Installation des dépendances Python non présentes dans les dépôts APT
---------------------------------------------------------------------

Même s'il est préférable d'installer les dépendances Python via les paquets APT,
tous ne sont malheureusement pas disponibles.

On doit donc récupérer les dépendances manquantes via pip.

Tout comme en développement, on préfère avoir un environnement virtuel dédié,
les ``sudo pip`` étant rarement compatibles avec les dépendances APT.

On construit donc un environnement virtuel et on installe les dépendances manquantes
dans cet environnement :

.. code:: bash

   $ cd /var/www/note_kfet
   $ python3 -m venv env
   $ . env/bin/activate
   (env) $ pip install -r requirements.txt

Normalement, seules les dépendances manquantes sont installées, les autres sont trouvées
globalement.

Plus d'informations sur les environnements virtuels dans la documentation officielle
de Python : `<https://docs.python.org/fr/3/tutorial/venv.html>`_.


Configuration de la note
------------------------

La configuration de la note se gère essentiellement via des paramètres d'environnement.
Ceux-ci sont lus via le fichier ``.env`` s'il existe, qui doit être placé à la racine
du projet cloné (donc dans ``/var/www/note_kfet/.env``). Un fichier d'exemple est situé
dans le fichier ``.env_example``, on peut donc faire un ``sudo cp .env_example .env``.

Attention aux permissions : le fichier doit être lu par ``www-data`` et écrit (rien
n'empêche de l'écrire en tant que root).

Le contenu de ce fichier :

.. code:: env

   DJANGO_APP_STAGE=prod
   DJANGO_DEV_STORE_METHOD=sqlite
   DJANGO_DB_HOST=localhost
   DJANGO_DB_NAME=note_db
   DJANGO_DB_USER=note
   DJANGO_DB_PASSWORD=CHANGE_ME
   DJANGO_DB_PORT=
   DJANGO_SECRET_KEY=CHANGE_ME
   DJANGO_SETTINGS_MODULE=note_kfet.settings
   CONTACT_EMAIL=tresorerie.bde@localhost
   NOTE_URL=localhost
   NOTE_MAIL=notekfet@localhost
   EMAIL_HOST=smtp.localhost
   EMAIL_PORT=25
   EMAIL_USER=notekfet@localhost
   EMAIL_PASSWORD=CHANGE_ME
   WIKI_USER=NoteKfet2020
   WIKI_PASSWORD=

Le paramètre ``DJANGO_APP_STAGE`` accepte comme valeur ``dev`` ou ``prod``.
En développement, les mails ne sont pas envoyés mais affichés dans les logs du
serveur. Les messages d'erreur sont directement affichés au lieu d'être envoyés
par mail. Les paramètres d'envoi de mail n'ont donc aucun effet. En développement,
il est également possible de choisir si l'on souhaite une base de données sqlite
(par défaut) ou si on veut se connecter à une base de données PostgreSQL (rentrer
``postgres`` dans ``DJANGO_DEV_STORE_METHOD``), auquel cas les paramètres de
base de données seront interprétés.

Les champs ``DJANGO_DB_`` sont relatifs à la connexion à la base de données PostgreSQL.

Le champ ``DJANGO_SECRET_KEY`` est utilisé pour la protection CSRF (voir la documentation
`<https://docs.djangoproject.com/fr/3.2/ref/csrf/>`_ pour plus de détails). Il s'agit d'une
clé sous forme de chaîne de caractère suffisamment longue (64 caractères paraît bien)
qui n'est pas à transmettre et qui évite d'autres sites malveillants de faire des requêtes
directement sur la note.

Le champ ``CONTACT_EMAIL`` correspond l'adresse mail que les adhérent⋅e⋅s peuvent contacter
en cas de problème. C'est là où le champ ``Nous contacter`` redirigera.

Le champ ``NOTE_URL`` correspond au nom de domaine autorisé à accéder au site. C'est également
le nom de domaine qui sera utilisé dans l'envoi de mails pour générer des liens. En
production, cela vaut ``note.crans.org``.

Le champ ``NOTE_MAIL`` correspond au champ expéditeur des mails envoyés, que ce soit
pour les rapports quotidiens / hebdomadaires / mensuels ou les mails d'erreur.
En production, ce champ vaut ``notekfet2020@crans.org``.

Les champs ``EMAIL_`` sont relatifs à la connexion au serveur SMTP pour l'envoi de mails.
En production, ``EMAIL_HOST`` vaut ``smtp.crans.org``, ``EMAIL_PORT`` vaut 25 (on reste sur
le réseau interne du Crans) et ``EMAIL_USER`` et ``EMAIL_PASSWORD`` sont vides (ce qui est
valide car la note est sur le réseau du Crans, qui est déjà pré-autorisé à envoyer des mails).

Les champs ``WIKI_USER`` et ``WIKI_PASSWORD`` servent à s'authentifier sur le compte Wiki
Crans ``NoteKfet2020``, pour notamment exporter automatiquement la liste des activités sur
le wiki.

Pour configurer la note, il est également possible de créer un fichier
``note_kfet/settings/secrets.py`` qui redéfinit certains paramètres, notamment la
liste des administrateurs ou certaines applications optionnelles, ou encore certains
éventuels mots de passe.

En production, ce fichier contient :

.. code:: python

   OPTIONAL_APPS = [
      'cas_server',
   #    'debug_toolbar'
   ]

   # When a server error occured, send an email to these addresses
   ADMINS = (
       ('Note Kfet', 'notekfet2020@lists.crans.org'),
   )


Configuration des tâches récurrentes
------------------------------------

Certaines opérations se font périodiquement, comme le rappel hebdomadaire pour les
personnes en négatif. On utilise pour cela un cron. Il suffit pour cela de copier
le fichier ``note.cron`` vers ``/etc/cron.d/note``, en veillant à ce qu'il appartienne
bien à ``root``.

Ce fichier contient l'ensemble des tâches récurrentes associées à la note.
Une page de documentation dédiée fera bientôt son apparition.

Sur un serveur de pré-production, on peut ne pas souhaiter activer ces tâches récurrentes.


Installation de la base de données PostgreSQL
---------------------------------------------

En production, on utilise une vraie base de données PostgreSQL et non un fichier
sqlite. Beaucoup plus facile pour faire éventuellement des requêtes (bien que pas
adapté pour Django) mais surtout bien mieux optimisé pour un serveur de production.

Pour installer la base de données, on commence par installer PostgreSQL :

.. code:: bash

   $ sudo apt install --no-install-recommends postgresql postgresql-contrib

PostgreSQL est désormais installé et lancé. On crée un compte ``note``, avec un
bon mot de passe (le même que donné à Django) :

.. code:: bash

   $ sudo -u postgres createuser -P note

Et on crée enfin une base de données nommée ``note_db`` appartenant à ``note``.

.. code:: bash

   $ sudo -u postgres createdb note_db -O note

La base de données est désormais prête à être utilisée.


Finir l'installation de Django
------------------------------

On commence par construire la base de données à partir des migrations enregistrées :

.. code:: bash

   $ ./manage.py migrate

On doit compiler les traductions (pour pouvoir les lire plus vite par la suite) :

.. code:: bash

   $ ./manage.py compilemessages

Les fichiers statiques (fiches de style, fichiers Javascript, images, ...) doivent
être exportées dans le dossier ``static`` :

.. code:: bash

   $ ./manage.py collectstatic

Et on peut enfin importer certaines données de base :

.. code:: bash

   $ ./manage.py loaddata initial

La note est désormais prête à être utilisée. Ne reste qu'à configurer un serveur Web.


Configuration de UWSGI
----------------------

On dispose d'une instance de la note fonctionnelle et bien configurée. Cependant, nous
n'avons pas encore de socket permettant d'intéragir avec le serveur. C'est le travail
de UWSGI.

On rappelle que la commande ``./manage.py runserver`` n'est pas conçue pour des serveurs
de production, contrairement à UWSGI.

On commence par installer UWSGI :

.. code:: bash

   $ sudo apt install --no-install-recommends uwsgi uwsgi-plugin-python3

On place ensuite le fichier de configuration UWSGI dans les applications installées.
Un fichier de configuration est présent à la racine du projet, contenant :

.. code:: ini

   [uwsgi]
   uid             = www-data
   gid             = www-data
   # Django-related settings
   # the base directory (full path)
   chdir           = /var/www/note_kfet
   # the virtualenv (full path)
   home            = /var/www/note_kfet/env
   wsgi-file       = /var/www/note_kfet/note_kfet/wsgi.py
   plugin          = python3
   # process-related settings
   # master
   master          = true
   # maximum number of worker processes
   processes       = 10
   # the socket (use the full path to be safe
   socket          = /var/www/note_kfet/note_kfet.sock
   # ... with appropriate permissions - may be needed
   chmod-socket    = 664
   # clear environment on exit
   vacuum          = true
   # Touch reload
   touch-reload    = /var/www/note_kfet/note_kfet/settings/__init__.py
   # Enable threads
   enable-threads  = true

Il suffit donc de créer le lien symbolique :

.. code:: bash

   $ sudo ln -s /var/www/note_kfet/uwsgi_note.ini /etc/uwsgi/apps-enabled/uwsgi_note.ini

On peut désormais relancer UWSGI :

.. code:: bash

   $ sudo systemctl restart uwsgi


Configuration de NGINX
----------------------

Nous avons désormais un socket qui nous permet de faire des connexions au serveur web,
placé dans ``/var/www/note_kfet/note_kfet.sock``. Cependant, ce socket n'est pas accessible
au reste du monde, et ne doit pas l'être : on veut un serveur Web Nginx qui s'occupe des
connexions entrantes et qui peut servir de reverse-proxy, notamment utile pour desservir
les fichiers statiques ou d'autres sites sur le même serveur.

On commence donc par installer Nginx :

.. code:: bash

   $ sudo apt install nginx

On place ensuite dans ``/etc/nginx/sites-available/nginx_note.conf`` le fichier de
configuration Nginx qui va bien, en remplaçant ``note.crans.org`` par ce qu'il faut :

.. code::

    # the upstream component nginx needs to connect to
    upstream note {
        server unix:///var/www/note_kfet/note_kfet.sock; # file socket
    }

    # Redirect HTTP to nk20 HTTPS
    server {
        listen 80 default_server;
        listen [::]:80 default_server;

        location / {
            return 301 https://note.crans.org$request_uri;
        }
    }

    # Redirect all HTTPS to nk20 HTTPS
    server {
        listen 443 ssl default_server;
        listen [::]:443 ssl default_server;

        location / {
            return 301 https://note.crans.org$request_uri;
        }

        ssl_certificate /etc/letsencrypt/live/note.crans.org/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/note.crans.org/privkey.pem;
        include /etc/letsencrypt/options-ssl-nginx.conf;
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    }

    # configuration of the server
    server {
        listen 443 ssl;
        listen [::]:443 ssl;

        # the port your site will be served on
        # the domain name it will serve for
        server_name note.crans.org;
        charset     utf-8;

        # max upload size
        client_max_body_size 75M;

        # Django media
        location /media  {
            alias /var/www/note_kfet/media;
        }

        location /static {
            alias /var/www/note_kfet/static;
        }

        location /doc {
            alias /var/www/documentation;
        }

        # Finally, send all non-media requests to the Django server.
        location / {
            uwsgi_pass note;
            include /etc/nginx/uwsgi_params;
        }

        ssl_certificate /etc/letsencrypt/live/note.crans.org/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/note.crans.org/privkey.pem;
        include /etc/letsencrypt/options-ssl-nginx.conf;
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    }

On peut enfin activer le site :

.. code::

   $ sudo ln -s /etc/nginx/sites-available/nginx_note.conf /etc/nginx/sites-enabled/nginx_note.conf

Si on peut se dire que recharger Nginx suffira, il n'en est rien : voir paragraphe suivant.


Génération d'un certificat SSL
------------------------------

Nginx va essayer de lire les certificats présents dans
``/etc/letsencrypt/live/note.crans.org/``, mais ce dossier n'existe pas encore.

On doit donc générer un certificat pour permettre les connexions HTTPS. Cela est permis
grâce à ``certbot``, qu'on s'empresse d'installer :

.. code:: bash

   $ sudo apt install certbot python3-certbot-nginx

Le plugin pour nginx permet de certifier que le serveur a bien les droits pour
``note.crans.org`` grâce à Nginx, le BDE n'ayant a priori aucune raison de pouvoir
gérer le nom de domaine ``crans.org``.

On place dans le dossier ``/etc/letsencrypt/conf.d`` (qu'on crée au besoin) un fichier
nommé ``nk20.ini`` :

.. code:: ini

    # To generate the certificate, please use the following command
    # certbot --config /etc/letsencrypt/conf.d/nk20.ini certonly

    # Use a 4096 bit RSA key instead of 2048
    rsa-key-size = 4096

    # Always use the staging/testing server
    # server = https://acme-staging.api.letsencrypt.org/directory

    # Uncomment and update to register with the specified e-mail address
    email = notekfet2020@lists.crans.org

    # Uncomment to use a text interface instead of ncurses
    text = True

    # Use Nginx challenge
    authenticator = nginx

En exécutant ``certbot``, il va lire les fichiers de configuration Nginx et générer les
certificats qu'il faut en créant un point d'entrée pour le serveur.

Il faut néanmoins que la configuration soit valide. Les certificats n'existant pas encore,
la configuration nginx est donc pour l'instant invalide. Il faut alors temporairement
commenter les parties de la configuration qui traitent des certificats et relancer ``nginx``
(``sudo systemctl reload nginx``).

On peut ensuite exécuter ``certbot`` :

.. code:: bash

   $ certbot --config /etc/letsencrypt/conf.d/nk20.ini certonly

L'instruction ``certonly`` indique à ``certbot`` qu'il se contente de générer le certificat,
sans chercher à l'installer. Si tout s'est bien passé, l'installation se fait simplement
en décommentant les lignes préalablement commentées.

Un certificat généré de la sorte expire au bout de 3 mois. Néanmoins, certbot tourne
régulièrement pour renouveler les certificats actifs automatiquement. Il n'y a donc
plus rien à faire.

Après avoir rechargé la configuration de ``Nginx``, rendez-vous sur
`<https://note.crans.org>`_ (ou votre site) pour vérifier que tout fonctionne correctement :)


Mettre à jour la note
---------------------

Pour mettre à jour la note, il suffit a priori, après avoir mis à jour les paquets APT,
de faire un ``git pull`` dans le dossier ``/var/www/note_kfet``.

Les éventuelles nouvelles migrations de la base de données doivent être appliquées :

.. code:: bash

   $ ./manage.py migrate

Les nouvelles traductions compilées :

.. code:: bash

   $ ./manage.py compilemessages

Les nouveaux fichiers statiques collectés :

.. code:: bash

   $ ./manage.py collectstatic

Et enfin les nouvelles fixtures installées :

.. code:: bash

   $ ./manage.py loaddata initial

Une fois tout cela fait, il suffit de relancer le serveur UWSGI :

.. code:: bash

   $ sudo systemctl restart uwsgi


Avec Ansible
------------

Tout ce travail peut sembler très laborieux et peut mériter d'être automatisé.
Toutefois, il est essentiel de bien comprendre comment chaque étape de l'installation
fonctionne.

Un playbook Ansible a été écrit permettant de réaliser toutes les tâches décrites ci-dessus.
Il se trouve dans le dossier ``ansible``.

Ansible s'installe sur votre propre machine (et non sur le serveur) en installant simplement
le paquet ``ansible``.

Pour déployer la note sur un serveur vierge, commencez par copier le fichier ``hosts_example``
en le nommant ``hosts``. Ajoutez votre propre serveur, dans la section correspondante.

Dans le dossier ``host_vars``, créez un fichier dont le nom est l'adresse du serveur, avec
l'extension ``.yml``.

Dans ce fichier, remplissez :

.. code:: yaml

   ---
   note:
     server_name: note.crans.org
     git_branch: master
     cron_enabled: true
     email: notekfet2020@lists.crans.org


en adaptant à votre configuration.

Il suffit ensuite de lancer ``./base.yml -l urldevotreserveur``.

Pour une première installation, vous devrez renseigner le mot de passe de la base de données
pour créer le compte ``note``. Vous devrez ensuite également refaire quelques ajustements
pour générer le certificat, voir la partie ``certbot``. La configuration du fichier
``.env`` sera également à faire à la main.

Cependant, pour mettre à jour, lancer cette commande suffit.
