Consommations
=============

Affichage
---------

La page de consommations est principalement une communication entre l'`API <../api>`_ et la page en JavaScript.
Elle est disponible à l'adresse ``/note/consos/``, et l'onglet n'est visible que pour ceux ayant le droit de voir au
moins un bouton. L'affichage, comme tout le reste de la page, est géré avec Boostrap 4.
Les boutons que l'utilisateur a le droit de voir sont triés par catégorie.

Sélection des consommations
---------------------------

Lorsque l'utilisateur commence à taper un nom de note, un appel à l'API sur la page ``/api/note/alias`` est fait,
récupérant les 20 premiers aliases en accord avec la requête. Quand l'utilisateur survole un alias, un appel à la page
``/api/note/note/<NOTE_ID>/`` est fait pour récupérer plus d'infos sur la note telles que le solde, le vrai nom de la
note et la photo, si toutefois l'utilisateur a le droit de voir ceci.

L'utilisateur peut cliquer sur des aliases pour ajouter des émetteurs, et sur des boutons pour ajouter des consommations.
Cliquer dans la liste des émetteurs supprime l'élément sélectionné.

Il ya deux possibilités pour faire consommer des adhérents :
  - En mode **consommation simple** (mode par défaut), les consommations sont débitées dès que émetteurs et consommations
    sont renseignées.
  - En mode **consommation double**, l'utilisateur doit cliquer sur "Consommer !" pour débiter toutes les consommations.

Débit des consommations
-----------------------

Pour débiter toutes les consommations, pour chaque source et chaque bouton, une requête POST est faite à l'API sur
l'adresse ``/api/note/transaction/transaction/`` avec le contenu suivant :

.. code:: json

    {
        "quantity": "<QUANTITÉ>",
        "amount": "<PRIX_EN_CENTIMES>",
        "reason": "<NOM_DU_BOUTON> (<CATÉGORIE_DU_BOUTON>)",
        "valid": true,
        "polymorphic_ctype": 42,
        "source": "<ID_DE_NOTE_SOURCE>",
        "destination": "<ID_DE_NOTE_DESTINATION>",
        "template": "<ID_BOUTON>",
        "category": "<ID_CATÉGORIE>",
        "resourcetype": "RecurrentTransaction"
    }

Par exemple, pour 3 cocas à 1.10 € (catégorie Soft, numéro 1), bouton numéro 1, à destination de la note Kfet (id 6)
depuis la note 7, la requête suivante est envoyée :

.. code:: json

    {
        "quantity": 3,
        "amount": 110,
        "reason": "Coca (Soft)",
        "valid": true,
        "polymorphic_ctype": 42,
        "source": 7,
        "destination": 6,
        "template": 1,
        "category": 1,
        "resourcetype": "RecurrentTransaction"
    }

Le ``42`` dans ``"polymorphic_ctype": 42`` correspond à l'identifiant du modèle `RecurrentTransaction` dans la table
des types. Il vaut `42` lors de la rédaction de cette documentation, mais pourra varier à l'avenir, et sera toujours
à jour : la valeur n'est pas "hard-codée".

Si une erreur survient lors de la requête (droits insuffisants), un message apparaîtra en haut de page.
Dans tous les cas, tous les champs sont réinitialisés.

L'historique et la balance de l'utilisateur sont ensuite mis à jour via jQuery, qui permet de recharger une partie de page Web.

Validation/dévalidation des transactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Il est possible aussi de (dé)valider une transaction en cliquant sur le symbole de validation. Lorsqu'un clic est fait,
une requête PATCH est faite à l'API sur l'adresse ``/api/note/transaction/transaction/<TRANSACTION_ID>/`` de la forme :

.. code:: json

    {
        "resourcetype": "RecurrentTransaction",
        "valid": false
    }

L'historique et la balance sont ensuite rafraîchis. Si une erreur survient, un message apparaîtra.
