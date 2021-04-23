Installer la Note Kfet sur sa propre machine
============================================

Jamais en production tu ne coderas.

Pour pouvoir développer sur la Note, il est donc essentiel de pouvoir installer
localement une instance de la note, avec une base de données vierge et indépendante
de celle utilisée en production.

Toutes les dépendances Python seront installées dans un environnement virtuel,
afin de ne pas polluer sa machine de dépendances de la note.


Dépendances de base
-------------------

On a néanmoins besoin de dépendances de base.

Sur un Ubuntu/Debian :

.. code:: bash

   $ sudo apt update
   $ sudo apt install --no-install-recommends -y \
       python3-setuptools python3-venv python3-dev \
       texlive-xetex gettext libjs-bootstrap4 fonts-font-awesome git

Pour Arch Linux :

.. code:: bash

   $ sudo pacman -Sy python-setuptools python-virtualenv \
       texlive-most gettext git

Bootstrap 4 n'est pas dans les paquets officiels de Arch Linux, mais peut-être
trouvé dans l'AUR grâce au paquet ``bootstrap``. Néanmoins, il faut pour l'instant
penser à créer un lien symbolique :
``sudo ln -s /usr/share/javascript/bootstrap /usr/share/javascript/bootstrap4``.

Néanmoins, font-awesome n'est pas disponible dans les paquets Arch Linux, mais non
essentiel en développement (n'ajoute que les symbole à côté des boutons).

À noter que bootstrap et texlive sont optionnels également selon vos besoins.


Téléchargement de la note
-------------------------

On récupère le dépôt Git de la note :

.. code:: bash

   $ git clone git@gitlab.crans.org:bde/nk20.git
   Clonage dans 'nk20'...
   remote: Enumerating objects: 203, done.
   remote: Counting objects: 100% (203/203), done.
   remote: Compressing objects: 100% (125/125), done.
   remote: Total 13438 (delta 98), reused 170 (delta 74), pack-reused 13235
   Réception d\'objets: 100% (13438/13438), 9.39 Mio | 5.50 Mio/s, fait.
   Résolution des deltas: 100% (9028/9028), fait.
   $ cd nk20

.. note::

   Pour apprendre à utiliser Git, on peut regarder la page wiki dédiée :
   `<https://wiki.crans.org/WikiInformatique/HowToGit>`_,
   ou bien regarder les séminaires Crans dédiés :
   `<https://wiki.crans.org/CransTechnique/CransApprentis/SeminairesTechniques>`_


Création d'un environnement virtuel Python
------------------------------------------

Une fois le projet cloné, on peut créer un environnement virtuel qui contiendra
toutes les dépendances Python.

Pour cela, on peut simplement faire :

.. code:: bash

   $ python3 -m venv env
   $ source env/bin/activate
   (env) $

À noter que ``source`` peut s'abbréger par ``.`` uniquement.

Vous êtes donc dans un environnement virtuel Python. Pour installer les dépendances
de la note :

.. code:: bash

   (env) $ pip install -r requirements.txt

Les dépendances s'installeront ensuite dans le dossier ``env``.

Au besoin, l'environnement peut être quitté en tapant ``deactivate`` et rejoint en
resourçant ``env/bin/activate``.

Plus d'informations sur les environnements virtuels dans la documentation officielle
de Python : `<https://docs.python.org/fr/3/tutorial/venv.html>`_.


Lancement de la note
--------------------

La partie Python (qui peut s'appliquer au développement de n'importe quel projet
Python) est terminée, on peut commencer à s'occuper de Django.

Pour rappel, Django est un cadre de développement web open source en Python extrêment
puissant. Il a pour but de rendre le développement web simple et rapide.

La documentation officielle de Django, complète, excellente et même en français,
peut être trouvée ici : `<https://docs.djangoproject.com/fr/>`_.

Pour lancer un serveur de développement, on peut donc commencer par compiler les
traductions :

.. code:: bash

   (env) $ ./manage.py compilemessages

On applique les migrations de la base de données (de test, qui sera créée) :

.. code:: bash

   (env) $ ./manage.py migrate

On importe quelques données de base et utiles :

.. code:: bash

   (env) $ ./manage.py loaddata initial

.. note::

   Ces données sont stockées au format JSON dans les différents fichiers
   ``apps/{app}/fixtures/initial.json``.

Enfin, on peut lancer le serveur web de développement :

.. code:: bash

   (env) $ ./manage.py runserver
   Watching for file changes with StatReloader
   Performing system checks...

   System check identified no issues (0 silenced).
   April 15, 2021 - 15:14:37
   Django version 2.2.20, using settings 'note_kfet.settings'
   Starting development server at http://127.0.0.1:8000/
   Quit the server with CONTROL-C.

Ouvrez votre navigateur, tapez `<http://localhost:8000/>`_, enjoy :)

.. note::

   En lançant le serveur web de la sorte, Django va recevoir un signal dès lors qu'un
   fichier a été modifié. Vous n'avez donc pas besoin de redémarrer le serveur après
   chaque modification, sauf erreurs.

   Attention : ce serveur n'est destiné qu'à des fins de développement et n'est pas
   optimisé pour recevoir des requêtes en parallèle ou être utilisé en production.


Créer un super-utilisateur
--------------------------

La commande ``./manage.py createsuperuser`` vous permettra de créer un super-utilisateur
initial.
