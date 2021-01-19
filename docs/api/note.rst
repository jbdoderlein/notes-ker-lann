API Note
========

Note
----

**Chemin :** `/api/note/note/ <https://note.crans.org/api/note/note/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Note Polymorphic List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Note` objects (with polymorhism),\nserialize it to JSON with the given serializer,\nthen render it on /api/note/note/",
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
          "POST": {}
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``alias__name``
* ``polymorphic_ctype``
* ``is_active``
* ``balance``
* ``last_negative``
* ``created_at``

Tris possible
~~~~~~~~~~~~~

* ``alias__name``
* ``alias__normalized_name``
* ``balance``
* ``created_at``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``alias__normalized_name`` (expression régulière)
* ``alias__name`` (expression régulière)
* ``polymorphic_ctype__model`` (expression régulière)
* ``noteuser__user__last_name`` (expression régulière)
* ``noteuser__user__first_name`` (expression régulière)
* ``noteuser__user__email`` (expression régulière)
* ``noteuser__user__email`` (expression régulière)
* ``noteclub__club__email`` (expression régulière)

Alias
-----

**Chemin :** `/api/note/alias/ <https://note.crans.org/api/note/alias/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Alias List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Alias` objects, serialize it to JSON with the given serializer,\nthen render it on /api/aliases/",
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
              "normalized_name": {
                  "type": "string",
                  "required": false,
                  "read_only": true,
                  "label": "Normalized name"
              },
              "note": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Note"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``note``
* ``note__noteuser__user``
* ``note__noteclub__club``
* ``note__polymorphic_ctype__model``

Tris possible
~~~~~~~~~~~~~

* ``name``
* ``normalized_name``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``alias`` (cherche en priorité les alias les plus proches, puis cherche les alias normalisés)
* ``normalized_name`` (expression régulière)
* ``name`` (expression régulière)
* ``note__polymorphic_ctype__model`` (expression régulière)

Consommateur
------------

**Chemin :** `/api/note/consumer/ <https://note.crans.org/api/note/consumer/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Consumer List",
      "description": "",
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

.. note::

   Cette page est en lecture seule. Elle offre l'avantage de fournir directement les informations sur la note associée
   à l'alias au lieu de l'identifiant uniquement, afin de minimiser les appels à l'API.

Filtres Django
~~~~~~~~~~~~~~

* ``alias`` (expression régulière, cherche en priorité les alias les plus proches, puis cherche les alias normalisés)
* ``note``
* ``note__noteuser__user``
* ``note__noteclub__club``
* ``note__polymorphic_ctype__model``

Tris possible
~~~~~~~~~~~~~

* ``name``
* ``normalized_name``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``normalized_name`` (expression régulière)
* ``name`` (expression régulière)
* ``note__polymorphic_ctype__model`` (expression régulière)

Catégorie de transaction
------------------------

**Chemin :** `/api/note/transaction/category/ <https://note.crans.org/api/note/transaction/category/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Template Category List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `TemplateCategory` objects, serialize it to JSON with the given serializer,\nthen render it on /api/note/transaction/category/",
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
                  "max_length": 31
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``templates``
* ``templates__name``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)
* ``templates__name`` (expression régulière)

Modèle de transaction
---------------------

**Chemin :** `/api/note/transaction/template/ <https://note.crans.org/api/note/transaction/template/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Transaction Template List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `TransactionTemplate` objects, serialize it to JSON with the given serializer,\nthen render it on /api/note/transaction/template/",
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
              "amount": {
                  "type": "integer",
                  "required": true,
                  "read_only": false,
                  "label": "Montant",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "display": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Afficher"
              },
              "highlighted": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Mis en avant"
              },
              "description": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Description",
                  "max_length": 255
              },
              "destination": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Destination"
              },
              "category": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Type"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``name``
* ``amount``
* ``display``
* ``category``
* ``category__name``

Tris possible
~~~~~~~~~~~~~

* ``amount``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)
* ``category__name`` (expression régulière)

Transaction
-----------

**Chemin :** `/api/note/transaction/transaction/ <https://note.crans.org/api/note/transaction/transaction/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Transaction List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Transaction` objects, serialize it to JSON with the given serializer,\nthen render it on /api/note/transaction/transaction/",
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
          "POST": {}
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``source``
* ``source_alias``
* ``source__alias__name``
* ``source__alias__normalized_name``
* ``destination``
* ``destination_alias``
* ``destination__alias__name``
* ``destination__alias__normalized_name``
* ``quantity``
* ``polymorphic_ctype``
* ``amount``
* ``created_at``
* ``valid``
* ``invalidity_reason``

Tris possible
~~~~~~~~~~~~~

* ``created_at``
* ``amount``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``reason`` (expression régulière)
* ``source_alias`` (expression régulière)
* ``source__alias__name`` (expression régulière)
* ``source__alias__normalized_name`` (expression régulière)
* ``destination_alias`` (expression régulière)
* ``destination__alias__name`` (expression régulière)
* ``destination__alias__normalized_name`` (expression régulière)
* ``invalidity_reason`` (expression régulière)

