Applications de la NoteKfet2020
===============================

.. toctree::
   :maxdepth: 2
   :caption: Applications

   member
   note/index
   activity
   permission
   ../api/index
   registration
   logs
   treasury
   wei

La NoteKfet est un projet Django, décomposé en applications.
Certaines Applications sont développées uniquement pour ce projet, et sont indispensables,
d'autres sont packagesé et sont installées comme dépendances.
Enfin des fonctionnalités annexes ont été rajouté, mais ne sont pas essentiel au déploiement de la NoteKfet;
leur usage est cependant recommandé.

Le front utilise le framework Bootstrap4 et quelques morceaux de javascript custom.

Applications indispensables
---------------------------

* ``note_kfet`` :
   Application "projet" de django, c'est ici que la config de la note est gérée.
* `Member <member>`_ :
   Gestion des profils d'utilisateurs, des clubs et de leur membres.
* `Note <note>`_ :
   Les notes associés a des utilisateurs ou des clubs.
* `Activity <activity>`_ :
   La gestion des Activités (créations, gestion, entrée...)
* `Permission <permission>`_ :
   Backend de droits, limites les pouvoirs des utilisateurs
* `API <../api>`_ :
   API REST de la note, est notamment utilisée pour rendre la note dynamique
   (notamment la page de conso)
* `Registration <registration>`_ :
   Gestion des inscriptions à la Note Kfet


Applications packagées
----------------------
* ``polymorphic``
    Utiliser pour la création de models polymorphiques (``Note`` et ``Transaction`` notamment) cf `Note <note>`_.

    L'utilisation des models polymorphiques est détaillé sur la documentation du package:
    `<https://django-polymorphic.readthedocs.io/en/stable/>`_

* ``crispy_forms``
    Utiliser pour générer des forms avec bootstrap4
* ``django_tables2``
    utiliser pour afficher des tables de données et les formater, en python plutôt qu'en HTML.
* ``restframework``
    Base de l'`API <../api>`_.

Applications facultatives
-------------------------
* `Logs <logs>`_
    Enregistre toute les modifications effectuées en base de donnée.
* ``cas-server``
    Serveur central d'authenfication, permet d'utiliser son compte de la NoteKfet2020 pour se connecter à d'autre application ayant intégrer un client.
* `Script <https://gitlab.crans.org/bde/nk20-scripts>`_
     Ensemble de commande `./manage.py` pour la gestion de la note: import de données, verification d'intégrité, etc ...
* `Treasury <treasury>`_ :
    Interface de gestion pour les trésoriers, émission de facture, remise de chèque, statistiques ...
* `WEI <wei>`_ :
    Interface de gestion du WEI.

