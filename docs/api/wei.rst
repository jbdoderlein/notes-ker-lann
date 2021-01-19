API WEI
=======

Wei
---

**Chemin :** `/api/wei/club/ <https://note.crans.org/api/wei/club/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Wei Club List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `WEIClub` objects, serialize it to JSON with the given serializer,\nthen render it on /api/wei/club/",
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
              "name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Nom",
                  "max_length": 255
              },
              "email": {
                  "type": "email",
                  "required": true,
                  "read_only": false,
                  "label": "Courriel",
                  "max_length": 254
              },
              "require_memberships": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "N\u00e9cessite des adh\u00e9sions",
                  "help_text": "D\u00e9cochez si ce club n'utilise pas d'adh\u00e9sions."
              },
              "membership_fee_paid": {
                  "type": "integer",
                  "required": false,
                  "read_only": false,
                  "label": "Cotisation pour adh\u00e9rer (normalien \u00e9l\u00e8ve)",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "membership_fee_unpaid": {
                  "type": "integer",
                  "required": false,
                  "read_only": false,
                  "label": "Cotisation pour adh\u00e9rer (normalien \u00e9tudiant)",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "membership_duration": {
                  "type": "integer",
                  "required": false,
                  "read_only": false,
                  "label": "Dur\u00e9e de l'adh\u00e9sion",
                  "help_text": "La dur\u00e9e maximale (en jours) d'une adh\u00e9sion (NULL = infinie).",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "membership_start": {
                  "type": "date",
                  "required": false,
                  "read_only": false,
                  "label": "D\u00e9but de l'adh\u00e9sion",
                  "help_text": "Date \u00e0 partir de laquelle les adh\u00e9rents peuvent renouveler leur adh\u00e9sion."
              },
              "membership_end": {
                  "type": "date",
                  "required": false,
                  "read_only": false,
                  "label": "Fin de l'adh\u00e9sion",
                  "help_text": "Date maximale d'une fin d'adh\u00e9sion, apr\u00e8s laquelle les adh\u00e9rents doivent la renouveler."
              },
              "year": {
                  "type": "integer",
                  "required": false,
                  "read_only": false,
                  "label": "Ann\u00e9e",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "date_start": {
                  "type": "date",
                  "required": true,
                  "read_only": false,
                  "label": "D\u00e9but"
              },
              "date_end": {
                  "type": "date",
                  "required": true,
                  "read_only": false,
                  "label": "Fin"
              },
              "parent_club": {
                  "type": "field",
                  "required": false,
                  "read_only": false,
                  "label": "Club parent"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``year``
* ``date_start``
* ``date_end``
* ``email``
* ``note__alias__name``
* ``note__alias__normalized_name``
* ``parent_club``
* ``parent_club__name``
* ``require_memberships``
* ``membership_fee_paid``
* ``membership_fee_unpaid``
* ``membership_duration``
* ``membership_start``
* ``membership_end``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)
* ``email`` (expression régulière)
* ``note__alias__name`` (expression régulière)
* ``note__alias__normalized_name`` (expression régulière)

Bus
---

**Chemin :** `/api/wei/bus/ <https://note.crans.org/api/wei/bus/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Bus List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Bus` objects, serialize it to JSON with the given serializer,\nthen render it on /api/wei/bus/",
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
              "name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Nom",
                  "max_length": 255
              },
              "description": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Description"
              },
              "information_json": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Informations sur le questionnaire",
                  "help_text": "Informations sur le sondage pour les nouveaux membres, encod\u00e9es en JSON"
              },
              "wei": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "WEI"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``wei``
* ``description``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)
* ``wei__name`` (expression régulière)
* ``description`` (expression régulière)

Équipe de bus
-------------

**Chemin :** `/api/wei/team/ <https://note.crans.org/api/wei/team/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Bus Team List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `BusTeam` objects, serialize it to JSON with the given serializer,\nthen render it on /api/wei/team/",
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
              "name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Nom",
                  "max_length": 255
              },
              "color": {
                  "type": "integer",
                  "required": true,
                  "read_only": false,
                  "label": "Couleur",
                  "help_text": "La couleur du T-Shirt, stock\u00e9 sous la forme de son \u00e9quivalent num\u00e9rique",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "description": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Description"
              },
              "bus": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Bus"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``bus``
* ``color``
* ``description``
* ``bus__wei``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)
* ``bus__name`` (expression régulière)
* ``bus__wei__name`` (expression régulière)
* ``description`` (expression régulière)

Rôle au wei
-----------

**Chemin :** `/api/wei/role/ <https://note.crans.org/api/wei/role/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Wei Role List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `WEIRole` objects, serialize it to JSON with the given serializer,\nthen render it on /api/wei/role/",
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
              "name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Nom",
                  "max_length": 255
              },
              "for_club": {
                  "type": "field",
                  "required": false,
                  "read_only": false,
                  "label": "S'applique au club"
              },
              "permissions": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Permissions"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``permissions``
* ``memberships``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)

Participant au wei
------------------

**Chemin :** `/api/wei/registration/ <https://note.crans.org/api/wei/registration/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Wei Registration List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all WEIRegistration objects, serialize it to JSON with the given serializer,\nthen render it on /api/wei/registration/",
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
              "soge_credit": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Cr\u00e9dit de la Soci\u00e9t\u00e9 g\u00e9n\u00e9rale"
              },
              "caution_check": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Ch\u00e8que de caution donn\u00e9"
              },
              "birth_date": {
                  "type": "date",
                  "required": true,
                  "read_only": false,
                  "label": "Date de naissance"
              },
              "gender": {
                  "type": "choice",
                  "required": true,
                  "read_only": false,
                  "label": "Genre",
                  "choices": [
                      {
                          "value": "male",
                          "display_name": "Homme"
                      },
                      {
                          "value": "female",
                          "display_name": "Femme"
                      },
                      {
                          "value": "nonbinary",
                          "display_name": "Non-binaire"
                      }
                  ]
              },
              "clothing_cut": {
                  "type": "choice",
                  "required": true,
                  "read_only": false,
                  "label": "Coupe de v\u00eatement",
                  "choices": [
                      {
                          "value": "male",
                          "display_name": "Homme"
                      },
                      {
                          "value": "female",
                          "display_name": "Femme"
                      }
                  ]
              },
              "clothing_size": {
                  "type": "choice",
                  "required": true,
                  "read_only": false,
                  "label": "Taille de v\u00eatement",
                  "choices": [
                      {
                          "value": "XS",
                          "display_name": "XS"
                      },
                      {
                          "value": "S",
                          "display_name": "S"
                      },
                      {
                          "value": "M",
                          "display_name": "M"
                      },
                      {
                          "value": "L",
                          "display_name": "L"
                      },
                      {
                          "value": "XL",
                          "display_name": "XL"
                      },
                      {
                          "value": "XXL",
                          "display_name": "XXL"
                      }
                  ]
              },
              "health_issues": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Probl\u00e8mes de sant\u00e9"
              },
              "emergency_contact_name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Nom du contact en cas d'urgence",
                  "max_length": 255
              },
              "emergency_contact_phone": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "T\u00e9l\u00e9phone du contact en cas d'urgence",
                  "max_length": 32
              },
              "first_year": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Premi\u00e8re ann\u00e9e",
                  "help_text": "Indique si l'utilisateur est nouveau dans l'\u00e9cole."
              },
              "information_json": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Informations sur l'inscription",
                  "help_text": "Informations sur l'inscription (bus pour les 2A+, questionnaire pour les 1A), encod\u00e9es en JSON"
              },
              "user": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Utilisateur"
              },
              "wei": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "WEI"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``user``
* ``user__username``
* ``user__first_name``
* ``user__last_name``
* ``user__email``
* ``user__note__alias__name``
* ``user__note__alias__normalized_name``
* ``wei``
* ``wei__name``
* ``wei__email``
* ``wei__year``
* ``soge_credit``
* ``caution_check``
* ``birth_date``
* ``gender``
* ``clothing_cut``
* ``clothing_size``
* ``first_year``
* ``emergency_contact_name``
* ``emergency_contact_phone``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``user__username`` (expression régulière)
* ``user__first_name`` (expression régulière)
* ``user__last_name`` (expression régulière)
* ``user__email`` (expression régulière)
* ``user__note__alias__name`` (expression régulière)
* ``user__note__alias__normalized_name`` (expression régulière)
* ``wei__name`` (expression régulière)
* ``wei__email`` (expression régulière)
* ``health_issues`` (expression régulière)
* ``emergency_contact_name`` (expression régulière)
* ``emergency_contact_phone`` (expression régulière)

Adhésion au wei
---------------

**Chemin :** `/api/wei/membership/ <https://note.crans.org/api/wei/membership/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Wei Membership List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `BusTeam` objects, serialize it to JSON with the given serializer,\nthen render it on /api/wei/membership/",
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
              "date_start": {
                  "type": "date",
                  "required": false,
                  "read_only": false,
                  "label": "L'adh\u00e9sion commence le"
              },
              "date_end": {
                  "type": "date",
                  "required": false,
                  "read_only": false,
                  "label": "L'adh\u00e9sion finit le"
              },
              "fee": {
                  "type": "integer",
                  "required": true,
                  "read_only": false,
                  "label": "Cotisation",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "user": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Utilisateur"
              },
              "club": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Club"
              },
              "bus": {
                  "type": "field",
                  "required": false,
                  "read_only": false,
                  "label": "Bus"
              },
              "team": {
                  "type": "field",
                  "required": false,
                  "read_only": false,
                  "label": "\u00c9quipe"
              },
              "registration": {
                  "type": "field",
                  "required": false,
                  "read_only": false,
                  "label": "Inscription au WEI"
              },
              "roles": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "R\u00f4les"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``club__name``
* ``club__email``
* ``club__note__alias__name``
* ``club__note__alias__normalized_name``
* ``user__username``
* ``user__last_name``
* ``user__first_name``
* ``user__email``
* ``user__note__alias__name``
* ``user__note__alias__normalized_name``
* ``date_start``
* ``date_end``
* ``fee``
* ``roles``
* ``bus``
* ``bus__name``
* ``team``
* ``team__name``
* ``registration``

Tris possible
~~~~~~~~~~~~~

* ``id``
* ``date_start``
* ``date_end``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``club__name`` (expression régulière)
* ``club__email`` (expression régulière)
* ``club__note__alias__name`` (expression régulière)
* ``club__note__alias__normalized_name`` (expression régulière)
* ``user__username`` (expression régulière)
* ``user__last_name`` (expression régulière)
* ``user__first_name`` (expression régulière)
* ``user__email`` (expression régulière)
* ``user__note__alias__name`` (expression régulière)
* ``user__note__alias__normalized_name`` (expression régulière)
* ``roles__name`` (expression régulière)
* ``bus__name`` (expression régulière)
* ``team__name`` (expression régulière)

