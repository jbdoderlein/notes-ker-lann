API générale
============

Utilisateur
-----------

**Chemin :** `/api/user/ <https://note.crans.org/api/user/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "User List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,\nthen render it on /api/user/",
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
          "POST": {
              "id": {
                  "type": "integer",
                  "required": false,
                  "read_only": true,
                  "label": "ID"
              },
              "last_login": {
                  "type": "datetime",
                  "required": false,
                  "read_only": false,
                  "label": "Derni\u00e8re connexion"
              },
              "is_superuser": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Statut super-utilisateur",
                  "help_text": "Pr\u00e9cise que l'utilisateur poss\u00e8de toutes les permissions sans les assigner explicitement."
              },
              "username": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Pseudo",
                  "help_text": "Requis. 150 caract\u00e8res maximum. Uniquement des lettres, nombres et les caract\u00e8res \u00ab\u00a0@\u00a0\u00bb, \u00ab\u00a0.\u00a0\u00bb, \u00ab\u00a0+\u00a0\u00bb, \u00ab\u00a0-\u00a0\u00bb et \u00ab\u00a0_\u00a0\u00bb.",
                  "max_length": 150
              },
              "first_name": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Pr\u00e9nom",
                  "max_length": 30
              },
              "last_name": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Nom de famille",
                  "max_length": 150
              },
              "email": {
                  "type": "email",
                  "required": false,
                  "read_only": false,
                  "label": "Adresse \u00e9lectronique",
                  "max_length": 254
              },
              "is_staff": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Statut \u00e9quipe",
                  "help_text": "Pr\u00e9cise si l'utilisateur peut se connecter \u00e0 ce site d'administration."
              },
              "is_active": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Actif",
                  "help_text": "Pr\u00e9cise si l'utilisateur doit \u00eatre consid\u00e9r\u00e9 comme actif. D\u00e9cochez ceci plut\u00f4t que de supprimer le compte."
              },
              "date_joined": {
                  "type": "datetime",
                  "required": false,
                  "read_only": false,
                  "label": "Date d'inscription"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``id``
* ``username``
* ``first_name``
* ``last_name``
* ``email``
* ``is_superuser``
* ``is_staff``
* ``is_active``
* ``note__alias__name``
* ``note__alias__normalized_name``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``note__alias`` (expression régulière, cherche en priorité les alias les plus proches, puis cherche les alias normalisés)
* ``last_name`` (expression régulière)
* ``first_name`` (expression régulière)

Type de contenu
---------------

**Chemin :** `/api/models/ <https://note.crans.org/api/models/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Content Type List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `User` objects, serialize it to JSON with the given serializer,\nthen render it on /api/models/",
      "renders": [
          "application/json",
          "text/html"
      ],
      "parses": [
          "application/json",
          "application/x-www-form-urlencoded",
          "multipart/form-data"
      ]
  }

Filtres Django
~~~~~~~~~~~~~~

* ``id``
* ``app_label``
* ``model``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``app_label`` (expression régulière)
* ``model`` (expression régulière)

