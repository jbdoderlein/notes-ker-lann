Documentation
=============

La documentation est gérée grâce à Sphinx. Le thème est le thème officiel de
ReadTheDocs ``sphinx-rtd-theme``.

Générer localement la documentation
-----------------------------------

On commence par se rendre au bon endroit et installer les bonnes dépendances :

.. code:: bash

  cd docs
  pip install -r requirements.txt

La documentation se génère à partir d'appels à ``make``, selon le type de
documentation voulue.

Par exemple, ``make dirhtml`` construit la documentation web,
``make latexpdf`` construit un livre PDF avec cette documentation.


Documentation automatique
-------------------------

Ansible compile et déploie automatiquement la documentation du projet, dans
le rôle ``8-docs``. Le rôle installe dans le bon environnement les dépendances
nécessaires, puis appelle sphinx pour placer la documentation compilée dans
``/var/www/documentation`` :

.. code:: bash

  /var/www/note_kfet/env/bin/sphinx-build -b dirhtml /var/www/note_kfet/docs/ /var/www/documentation/

Ce dossier est exposé par ``nginx`` sur le chemin
`/doc <https://note.crans.org/doc>`_.
