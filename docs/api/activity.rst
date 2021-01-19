API Activités
=============

Activité
--------

**Chemin :** `/api/activity/activity/ <https://note.crans.org/api/activity/activity/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Activity List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Activity` objects, serialize it to JSON with the given serializer,\nthen render it on /api/activity/activity/",
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
                  "required": true,
                  "read_only": false,
                  "label": "Description"
              },
              "location": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Lieu",
                  "help_text": "Lieu o\u00f9 l'activit\u00e9 est organis\u00e9e, par exemple la Kfet.",
                  "max_length": 255
              },
              "date_start": {
                  "type": "datetime",
                  "required": true,
                  "read_only": false,
                  "label": "Date de d\u00e9but"
              },
              "date_end": {
                  "type": "datetime",
                  "required": true,
                  "read_only": false,
                  "label": "Date de fin"
              },
              "valid": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Valide"
              },
              "open": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Ouvrir"
              },
              "activity_type": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Type"
              },
              "creater": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Utilisateur"
              },
              "organizer": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Organisateur",
                  "help_text": "Le club qui organise l'activit\u00e9. Les co\u00fbts d'invitation iront pour ce club."
              },
              "attendees_club": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Club attendu",
                  "help_text": "Club qui est autoris\u00e9 \u00e0 rejoindre l'activit\u00e9. Tr\u00e8s souvent le club Kfet."
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``description``
* ``activity_type``
* ``location``
* ``creater``
* ``organizer``
* ``attendees_club``
* ``date_start``
* ``date_end``
* ``valid``
* ``open``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)
* ``description`` (expression régulière)
* ``location`` (expression régulière)
* ``creater__last_name`` (expression régulière)
* ``creater__first_name`` (expression régulière)
* ``creater__email`` (expression régulière)
* ``creater__note__alias__name`` (expression régulière)
* ``creater__note__alias__normalized_name`` (expression régulière)
* ``organizer__name`` (expression régulière)
* ``organizer__email`` (expression régulière)
* ``organizer__note__alias__name`` (expression régulière)
* ``organizer__note__alias__normalized_name`` (expression régulière)
* ``attendees_club__name`` (expression régulière)
* ``attendees_club__email`` (expression régulière)
* ``attendees_club__note__alias__name`` (expression régulière)
* ``attendees_club__note__alias__normalized_name`` (expression régulière)

Type d'activité
---------------

**Chemin :** `/api/activity/type/ <https://note.crans.org/api/activity/type/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Activity Type List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `ActivityType` objects, serialize it to JSON with the given serializer,\nthen render it on /api/activity/type/",
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
              "manage_entries": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "G\u00e9rer les entr\u00e9es",
                  "help_text": "Activer le support des entr\u00e9es pour cette activit\u00e9."
              },
              "can_invite": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Peut inviter"
              },
              "guest_entry_fee": {
                  "type": "integer",
                  "required": false,
                  "read_only": false,
                  "label": "Cotisation de l'entr\u00e9e invit\u00e9",
                  "min_value": 0,
                  "max_value": 2147483647
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``manage_entries``
* ``can_invite``
* ``guest_entry_fee``

Invité
------

**Chemin :** `/api/activity/guest/ <https://note.crans.org/api/activity/guest/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Guest List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Guest` objects, serialize it to JSON with the given serializer,\nthen render it on /api/activity/guest/",
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
              "last_name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Nom de famille",
                  "max_length": 255
              },
              "first_name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Pr\u00e9nom",
                  "max_length": 255
              },
              "activity": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Activity"
              },
              "inviter": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "H\u00f4te"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``activity``
* ``activity__name``
* ``last_name``
* ``first_name``
* ``inviter``
* ``inviter__alias__name``
* ``inviter__alias__normalized_name``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``activity__name`` (expression régulière)
* ``last_name`` (expression régulière)
* ``first_name`` (expression régulière)
* ``inviter__user__email`` (expression régulière)
* ``inviter__alias__name`` (expression régulière)
* ``inviter__alias__normalized_name`` (expression régulière)

Entrée
------

**Chemin :** `/api/activity/entry/ <https://note.crans.org/api/activity/entry/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Entry List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Entry` objects, serialize it to JSON with the given serializer,\nthen render it on /api/activity/entry/",
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
              "time": {
                  "type": "datetime",
                  "required": false,
                  "read_only": false,
                  "label": "Heure d'entr\u00e9e"
              },
              "activity": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Activit\u00e9"
              },
              "note": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Note"
              },
              "guest": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Guest"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``activity``
* ``time``
* ``note``
* ``guest``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``activity__name`` (expression régulière)
* ``note__user__email`` (expression régulière)
* ``note__alias__name`` (expression régulière)
* ``note__alias__normalized_name`` (expression régulière)
* ``guest__last_name`` (expression régulière)
* ``guest__first_name`` (expression régulière)

