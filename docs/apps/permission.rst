Droits
======

Le système de droit par défault de django n'est pas suffisament granulaire pour les besoins de la NoteKfet2020.
Un système custom a donc été développé.

Il permet la création de Permission, qui autorise ou non a faire une action précise sur un ou des objets
de la base de données.

Plusieurs permissions peuvent être regroupé dans un Role.
Ce Role est relié a la responsabilité/fonction de la personne dans un Club. Ils sont valable au maximum tant que la
personne est adhérente du Club concerné, mais ce rôle peut être modifié/supprimé avant le terme.

Permission
----------

Une permission est un Model Django dont les principaux attributs sont :

* ``model`` : Le model sur lequel cette permission va s'appliquer
* ``type``  : Les différents types d'interaction sont : voir (``view``), modifier (``change``), ajouter (``add``)
  et supprimer (``delete``).
* ``query`` : Requête sur la cible, encodé en JSON, traduit en un Q object (cf `Query <#compilation-de-la-query>`_)
* ``field`` : le champ cible qui pourra être modifié. (tous les champs si vide)

Pour savoir si un utilisateur a le droit sur un modèle ou non, la requête est compilée (voir ci-dessous) en un filtre
de requête dans la base de données, un objet de la classe ``Q`` (En SQL l'objet Q s'interprete comme tout ce qui suit
un ``WHERE ...`` Ils peuvent être combiné à l'aide d'opérateurs logiques. Plus d'information sur les Q object dans la
`documentation officielle <https://docs.djangoproject.com/fr/2.2/topics/db/queries/#complex-lookups-with-q-objects>`_.

Ce Q object sera donc utilisé pour savoir si l'instance que l'on veux modifier est concernée par notre permission.

Exception faite sur l'ajout d'objets : l'objet n'existant pas encore en base de données, il est ajouté puis supprimé
à la volée, en prenant soin de désactiver les signaux.

Compilation de la query
-----------------------

La query est enregistrée sous un format JSON, puis est traduite en requête ``Q`` récursivement en appliquant certains paramètres.
Le fonctionnemente de base des permission peux être décris avec les differents opérations :

+----------------+-----------------------------+-------------------------------------+
| opérations     | JSON                        | Q object                            |
+================+=============================+=====================================+
| ALL            | ``[]`` ou ``{}``            | ``.objects.get(Q(pk=F("pk"))``      |
+----------------+-----------------------------+-------------------------------------+
| ET             | ``["AND", Q_1, Q_2, ... ]`` | ``.objects.get(Q_1 & Q_2 & ...)``   |
+----------------+-----------------------------+-------------------------------------+
| OU             | ``["OR", Q_1, Q_2, ...]``   | ``.objects.get(Q_1 \| Q_2 \| ...)`` |
+----------------+-----------------------------+-------------------------------------+
| NON            | ``["NOT", Q_1]``            | ``.objects.get(~Q_1)``              |
+----------------+-----------------------------+-------------------------------------+
| key == value   | ``{key: value}``            | ``.objects.get(Q(key = value))``    |
+----------------+-----------------------------+-------------------------------------+


Vous n'avez rien compris ? Voilà des exemples :

Exemples
--------

* Permission sur le model ``User`` avec comme query:

  .. code:: js

    {"is_superuser": true}

  | si l'utilisateur cible est un super utilisateur.

* sur le model ``Note`` :

  .. code:: js

    {"pk":
      ["user","note", "pk"]
    }

  |  si l'identifiant de la note cible est l'identifiant de l'utilisateur dont on regarde la permission.

* sur le model ``Transaction``:

  .. code:: js

    ["AND",
      {"source":
        ["user", "note"]},
      {"amount__lte":
        ["user", "note", "balance"]}
    ]

  | si la source est la note de l'utilisateur et si le montant est inférieur à son solde.

* Sur le model ``Alias``

  .. code:: js

    ["OR",
      {"note__in":
        ["NoteUser", "objects",[
          "filter",{
            "user__membership__club__name": "Kfet"
          }],
          ["all"]
        ]},
      {"note__in":
        ["NoteClub", "objects", ["all"]]
      }
    ]

  | si l'alias appartient à une note de club ou s'il appartient à la note d'un utilisateur membre du club Kfet.

* sur le model ``Transaction``

  .. code:: js

    ["AND",
      {"destination": ["club", "note"]},
      {"amount__lte":
         {"F": [
           "ADD",
           ["F", "source__balance"],
           5000]
         }
       }
    ]

  | si la destination est la note du club dont on est membre et si le montant est inférieur au solde de la source + 50 €,
    autrement dit le solde final est au-dessus de -50 €.


Masques de permissions
----------------------

Chaque permission est associée à un masque. À la connexion, l'utilisateur choisit le masque de droits avec lequel il
souhaite se connecter. Les masques sont ordonnés totalement, et l'utilisateur aura effectivement une permission s'il est
en droit d'avoir la permission et si son masque est suffisamment haut.

Par exemple, si la permission de voir toutes les transactions est associée au masque "Droits note uniquement",
se connecter avec le masque "Droits basiques" n'octroiera pas cette permission tandis que le masque "Tous mes droits" oui.

Signaux
-------

À chaque fois qu'un modèle est modifié, ajouté ou supprimé, les droits sont contrôlés. Si les droits ne sont pas
suffisants, une erreur est lancée. Pour ce qui est de la modification, on ne contrôle que les champs réellement
modifiés en comparant l'ancienne et la nouvele instance.

Graphe des modèles
------------------

.. image:: /_static/img/graphs/permission.svg
   :alt: Graphe de l'application permission
