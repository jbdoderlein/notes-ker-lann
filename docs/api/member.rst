API Membres
===========

Profil utilisateur
------------------

**Chemin :** `/api/members/profile/ <https://note.crans.org/api/members/profile/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Profile List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Profile` objects, serialize it to JSON with the given serializer,\nthen render it on /api/members/profile/",
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
              "phone_number": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Num\u00e9ro de t\u00e9l\u00e9phone",
                  "max_length": 50
              },
              "section": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Section",
                  "help_text": "e.g. \"1A0\", \"9A\u2665\", \"SAPHIRE\"",
                  "max_length": 255
              },
              "department": {
                  "type": "choice",
                  "required": true,
                  "read_only": false,
                  "label": "D\u00e9partement",
                  "choices": [
                      {
                          "value": "A0",
                          "display_name": "Informatique (A0)"
                      },
                      {
                          "value": "A1",
                          "display_name": "Math\u00e9matiques (A1)"
                      },
                      {
                          "value": "A2",
                          "display_name": "Chimie (A''2)"
                      },
                      {
                          "value": "A'2",
                          "display_name": "Physique appliqu\u00e9e (A'2)"
                      },
                      {
                          "value": "A3",
                          "display_name": "Biologie (A3)"
                      },
                      {
                          "value": "B1234",
                          "display_name": "SAPHIRE (B1234)"
                      },
                      {
                          "value": "B1",
                          "display_name": "M\u00e9canique (B1)"
                      },
                      {
                          "value": "B2",
                          "display_name": "G\u00e9nie civil (B2)"
                      },
                      {
                          "value": "B3",
                          "display_name": "G\u00e9nie m\u00e9canique (B3)"
                      },
                      {
                          "value": "B4",
                          "display_name": "EEA (B4)"
                      },
                      {
                          "value": "C",
                          "display_name": "Design (C)"
                      },
                      {
                          "value": "D2",
                          "display_name": "\u00c9conomie-gestion (D2)"
                      },
                      {
                          "value": "D3",
                          "display_name": "Sciences sociales (D3)"
                      },
                      {
                          "value": "E",
                          "display_name": "Anglais (E)"
                      },
                      {
                          "value": "EXT",
                          "display_name": "Externe (EXT)"
                      }
                  ]
              },
              "promotion": {
                  "type": "integer",
                  "required": false,
                  "read_only": false,
                  "label": "Promotion",
                  "help_text": "Ann\u00e9e d'entr\u00e9e dans l'\u00e9cole (None si non-\u00e9tudiant\u00b7e de l'ENS)",
                  "min_value": 0,
                  "max_value": 32767
              },
              "address": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Adresse",
                  "max_length": 255
              },
              "paid": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Pay\u00e9",
                  "help_text": "Indique si l'utilisateur per\u00e7oit un salaire."
              },
              "ml_events_registration": {
                  "type": "choice",
                  "required": false,
                  "read_only": false,
                  "label": "S'inscrire sur la liste de diffusion pour rester inform\u00e9 des \u00e9v\u00e9nements sur le campus (1 mail par semaine)",
                  "choices": [
                      {
                          "value": "",
                          "display_name": "Non"
                      },
                      {
                          "value": "fr",
                          "display_name": "Oui (les recevoir en fran\u00e7ais)"
                      },
                      {
                          "value": "en",
                          "display_name": "Oui (les recevoir en anglais)"
                      }
                  ]
              },
              "ml_sport_registration": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "S'inscrire sur la liste de diffusion pour rester inform\u00e9 des actualit\u00e9s sportives sur le campus (1 mail par semaine)"
              },
              "ml_art_registration": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "S'inscrire sur la liste de diffusion pour rester inform\u00e9 des actualit\u00e9s artistiques sur le campus (1 mail par semaine)"
              },
              "report_frequency": {
                  "type": "integer",
                  "required": false,
                  "read_only": false,
                  "label": "Fr\u00e9quence des rapports (en jours)",
                  "min_value": 0,
                  "max_value": 32767
              },
              "last_report": {
                  "type": "datetime",
                  "required": false,
                  "read_only": false,
                  "label": "Date de dernier rapport"
              },
              "email_confirmed": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Adresse email confirm\u00e9e"
              },
              "registration_valid": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Inscription valide"
              },
              "user": {
                  "type": "field",
                  "required": false,
                  "read_only": true,
                  "label": "User"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``user``
* ``user__first_name``
* ``user__last_name``
* ``user__username``
* ``user__email``
* ``user__note__alias__name``
* ``user__note__alias__normalized_name``
* ``phone_number``
* ``section``
* ``department``
* ``promotion``
* ``address``
* ``paid``
* ``ml_events_registration``
* ``ml_sport_registration``
* ``ml_art_registration``
* ``report_frequency``
* ``email_confirmed``
* ``registration_valid``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``user__first_name`` (expression régulière)
* ``user__last_name`` (expression régulière)
* ``user__username`` (expression régulière)
* ``user__email`` (expression régulière)
* ``user__note__alias__name`` (expression régulière)
* ``user__note__alias__normalized_name`` (expression régulière)

Club
----

**Chemin :** `/api/members/club/ <https://note.crans.org/api/members/club/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Club List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Club` objects, serialize it to JSON with the given serializer,\nthen render it on /api/members/club/",
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

Adhésion
--------

**Chemin :** `/api/members/membership/ <https://note.crans.org/api/members/membership/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Membership List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Membership` objects, serialize it to JSON with the given serializer,\nthen render it on /api/members/membership/",
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

