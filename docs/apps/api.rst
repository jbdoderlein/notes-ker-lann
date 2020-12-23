API
===

La NoteKfet2020 dispose d'une API REST. Elle est accessible sur `/api/ <https://note.crans.org/api/>`_.
Elle supporte les requêtes GET, POST, HEAD, PUT, PATCH et DELETE (peut varier selon les pages).

Pages de l'API
--------------

Il suffit d'ajouter le préfixe ``/api/`` pour arriver sur ces pages.

* ``models`` (liste des différents modèles enregistrés en base de données)
* ``user`` (liste des différents utilisateurs enregistrés)
* ``members/profile`` (liste des différents profils associés à des utilisateurs)
* ``members/club`` (liste des différents clubs enregistrés)
* ``members/role`` (liste des différents rôles au sein des clubs existant)
* ``members/membership`` (liste des adhésions enregistrées)
* ``activity/activity`` (liste des activités recensées)
* ``activity/type`` (liste des différents types d'activités : pots, soirées de club, ...)
* ``activity/guest`` (liste des personnes invitées lors d'une activité)
* ``activity/entry`` (liste des entrées effectuées lors des activités)
* ``note/note`` (liste des notes enregistrées)
* ``note/alias`` (liste des alias enregistrés)
* ``note/transaction/category`` (liste des différentes catégories de boutons : soft, alcool, ...)
* ``note/transaction/transaction`` (liste des transactions effectuées)
* ``note/transaction/template`` (liste des boutons enregistrés)
* ``treasury/invoice`` (liste des factures générées)
* ``treasury/product`` (liste des produits associés à des factures)
* ``treasury/remittance_type`` (liste des types de remises supportés : chèque)
* ``treasury/remittance`` (liste des différentes remises enregistrées)
* ``permission/permission`` (liste de toutes les permissions enregistrées)
* ``permission/roles`` (liste des permissions octroyées pour chacun des rôles)
* ``logs`` (liste des modifications enregistrées en base de données)

Utilisation de l'API
--------------------

La page ``/api/<model>/`` affiche la liste de tous les éléments enregistrés. La page ``/api/<model>/<pk>/`` affiche
les attributs d'un objet uniquement.

L'affichage des données peut se faire sous deux formes : via une interface HTML propre ou directement en affichant
le JSON brut. Le changement peut se faire en ajoutant en paramètre de l'URL ``format=json`` ou ``format=api``, ou bien
en plaçant en en-tête de la requête ``Accept: application/json`` ou ``Accept: text/html``.

L'API Web propose des formulaires facilitant l'ajout et la modification d'éléments.

S'authentifier
~~~~~~~~~~~~~~

L'authentification peut se faire soit par session en se connectant via la page de connexion classique,
soit via un jeton d'authentification. Le jeton peut se récupérer via la page de son propre compte, en cliquant
sur le bouton « `Accès API <https://note.crans.org/accounts/manage-auth-token/>`_ ». Il peut être révoqué et regénéré
en un clic.

Pour s'authentifier via ce jeton, il faut ajouter l'en-tête ``Authorization: Token <TOKEN>`` aux paramètres HTTP.

En s'authentifiant par cette méthode, les masques de droit sont ignorés, les droits maximaux sont accordés.

GET
~~~

Une requête GET affiche un ou des éléments. Si on veut la liste de tous les éléments d'un modèle, la réponse
est de cette forme :

.. code:: json

    {
        "count": "<COUNT>",
        "next": "/api/<MODEL>/?page=<NEXT_PAGE>",
        "previous": "/api/<MODEL>/?page=<NEXT_PAGE>",
        "results": [  ]
    }

Où ``<COUNT>`` est le nombre d'éléments trouvés. La page n'affiche les informations que 20 par 20 pour ne pas
augmenter inutilement la taille de la réponse. Les champs ``next`` et ``previous`` contiennent les URL des pages
suivantes et précédentes (``null`` si première ou dernière page). Le champ ``results`` contient enfin l'ensemble des
objets trouvés, au format JSON.

Certaines pages disposent de filtres, permettant de sélectionner les objets recherchés. Par exemple, il est possible
de chercher une note d'un certain type matchant avec un certain alias.

Le résultat est déjà par défaut filtré : seuls les éléments que l'utilisateur à le droit de voir sont affichés.
Cela est possible grâce à la structure des permissions, générant justement des filtres de requêtes de base de données.

Une requête à l'adresse ``/api/<model>/pk/`` affiche directement les informations du modèle demandé au format JSON.

POST
~~~~

Une requête POST permet d'ajouter des éléments. Cette requête n'est possible que sur la page ``/api/<model>/``,
la requête POST n'est pas supportée sur les pages de détails (car cette requête permet ... l'ajout).

Des exceptions sont faites sur certaines pages : les pages de logs et de contenttypes sont en lecture uniquement.

Les formats supportés sont multiples : ``application/json``, ``application/x-www-url-encoded``, ``multipart/form-data``.
Cela facilite l'envoi de requêtes. Le module construit ensuite l'instance du modèle et le sauvegarde dans la base de
données. L'application ``permission`` s'assure que l'utilisateur à le droit de faire ce type de modification. La réponse
renvoyée est l'objet enregistré au format JSON si l'ajout s'est bien déroulé, sinon un message d'erreur au format JSON.

PATCH
~~~~~

Une requête PATCH permet de modifier un élément. Ce type de requête n'est disponible que sur la page de détails d'un
élément : ``/api/<model>/pk/``.

Comme pour la requête POST, les formats supportés sont multiples : ``application/json``,
``application/x-www-url-encoded``, ``multipart/form-data``.

Il n'est pas utile d'indiquer tous les champs du modèle : seuls ceux qui sont à modifier suffisent.

Attention : pour les modèles polymorphiques (``Note``, ``Transaction``), il faut toujours spécifier le type de modèle
pour que l'API arrive à s'y retrouver. Par exemple, si on veut rendre la transaction n°42 non valide, on effectue une
requête ``PATCH`` sur ``/api/note/transaction/transaction/42/`` avec les données suivantes :

.. code:: json

    {
        "valid": false,
        "resourcetype": "RecurrentTransaction"
    }

PUT
~~~

Une requête PUT permet de remplacer un élément. Ce type de requête n'est disponible que sur la page de détails d'un
élément : ``/api/<model>/pk/``.

Comme pour les requêtes POST ou PATCH, les formats supportés sont multiples : ``application/json``,
``application/x-www-url-encoded``, ``multipart/form-data``.

Contrairement à la requête PATCH, l'intégralité du modèle est remplacé. L'ancien modèle est détruit, on en recrée un
nouveau avec la même clé primaire. Le fonctionnement est similaire à une requête POST.

DELETE
~~~~~~

Une requête de type DELETE permet de supprimer un élément. Ce type de requête n'est disponible que sur la page de
détails d'un élément : ``/api/<model>/pk/``.

Aucune donnée n'est nécessaire. Le module de permissions vérifiera que la suppression est possible. Une erreur
est sinon renvoyée.

OPTIONS
~~~~~~~

Une reqête OPTIONS affiche l'ensemble des opérations possibles sur un modèle ou une instance. Prototype d'une réponse :

.. code:: json

    {
        "name": "<NAME>",
        "description": "<DESCRIPTION>",
        "renders": [
            "application/json",
            "text/html"
        ],
        "parses": [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ],
        "actions": {
            "<METHOD>": {
                "<FIELD_NAME>": {
                    "type": "<TYPE>",
                    "required": "<REQUIRED>",
                    "read_only": "<READ_ONLY>",
                    "label": "<LABEL>"
                }
            }
        }
    }

* ``<METHOD>`` est le type de requête HTTP supporté (pour modification, inclus dans {``POST``, ``PUT``, ``PATCH``}).
* ``<FIELD_NAME>`` est le nom du champ dans le modèle concerné (exemple : ``id``)
* ``<TYPE>`` représente le type de données : ``integer``, ``string``, ``date``, ``choice``, ``field`` (pour les clés étrangères), ...
* ``<REQUIRED>`` est un booléen indiquant si le champ est requis dans le modèle ou s'il peut être nul/vide.
* ``<READ_ONLY>`` est un booléen indiquant si le champ est accessible en lecture uniquement.
* ``<LABEL>`` représente le label du champ, son nom traduit, qui s'affiche dans le formulaire accessible sur l'API Web.

Des contraintes peuvent s'ajouter à cela selon les champs : taille maximale de chaînes de caractères, valeurs minimales
et maximales pour les entiers ...