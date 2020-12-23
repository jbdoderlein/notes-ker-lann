API Trésorerie
==============

Facture
-------

**Chemin :** `/api/treasury/invoice/ <https://note.crans.org/api/treasury/invoice/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Invoice List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Invoice` objects, serialize it to JSON with the given serializer,\nthen render it on /api/treasury/invoice/",
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
                  "required": true,
                  "read_only": false,
                  "label": "Num\u00e9ro de facture",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "products": {
                  "type": "field",
                  "required": false,
                  "read_only": true,
                  "label": "Products"
              },
              "bde": {
                  "type": "choice",
                  "required": false,
                  "read_only": true,
                  "label": "BDE"
              },
              "object": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Objet",
                  "max_length": 255
              },
              "description": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Description"
              },
              "name": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Nom",
                  "max_length": 255
              },
              "address": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Adresse"
              },
              "date": {
                  "type": "date",
                  "required": false,
                  "read_only": false,
                  "label": "Date"
              },
              "acquitted": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Acquitt\u00e9e"
              },
              "locked": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Verrouill\u00e9e",
                  "help_text": "Une facture ne peut plus \u00eatre modifi\u00e9e si elle est verrouill\u00e9e."
              },
              "tex": {
                  "type": "string",
                  "required": false,
                  "read_only": false,
                  "label": "Fichier TeX source"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``bde``
* ``object``
* ``description``
* ``name``
* ``address``
* ``date``
* ``acquitted``
* ``locked``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``object`` (expression régulière)
* ``description`` (expression régulière)
* ``name`` (expression régulière)
* ``address`` (expression régulière)

Produit
-------

**Chemin :** `/api/treasury/product/ <https://note.crans.org/api/treasury/product/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Product List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Product` objects, serialize it to JSON with the given serializer,\nthen render it on /api/treasury/product/",
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
              "designation": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "D\u00e9signation",
                  "max_length": 255
              },
              "quantity": {
                  "type": "integer",
                  "required": true,
                  "read_only": false,
                  "label": "Quantit\u00e9",
                  "min_value": 0,
                  "max_value": 2147483647
              },
              "amount": {
                  "type": "integer",
                  "required": true,
                  "read_only": false,
                  "label": "Prix unitaire",
                  "min_value": -2147483648,
                  "max_value": 2147483647
              },
              "invoice": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Facture"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``invoice``
* ``designation``
* ``quantity``
* ``amount``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``designation`` (expression régulière)
* ``invoice__object`` (expression régulière)

Type de remise
--------------

**Chemin :** `/api/treasury/remittance_type/ <https://note.crans.org/api/treasury/remittance_type/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Remittance Type List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `RemittanceType` objects, serialize it to JSON with the given serializer\nthen render it on /api/treasury/remittance_type/",
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

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``note__special_type`` (expression régulière)

Remise
------

**Chemin :** `/api/treasury/remittance/ <https://note.crans.org/api/treasury/remittance/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Remittance List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Remittance` objects, serialize it to JSON with the given serializer,\nthen render it on /api/treasury/remittance/",
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
              "transactions": {
                  "type": "field",
                  "required": false,
                  "read_only": true,
                  "label": "Transactions"
              },
              "date": {
                  "type": "datetime",
                  "required": false,
                  "read_only": false,
                  "label": "Date"
              },
              "comment": {
                  "type": "string",
                  "required": true,
                  "read_only": false,
                  "label": "Commentaire",
                  "max_length": 255
              },
              "closed": {
                  "type": "boolean",
                  "required": false,
                  "read_only": false,
                  "label": "Ferm\u00e9e"
              },
              "remittance_type": {
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

* ``date``
* ``remittance_type``
* ``comment``
* ``closed``
* ``transaction_proxies__transaction``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``remittance_type__note__special_type`` (expression régulière)
* ``comment`` (expression régulière)

Crédit de la société générale
-----------------------------

**Chemin :** `/api/treasury/soge_credit/ <https://note.crans.org/api/treasury/soge_credit/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Soge Credit List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `SogeCredit` objects, serialize it to JSON with the given serializer,\nthen render it on /api/treasury/soge_credit/",
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
              "user": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Utilisateur"
              },
              "credit_transaction": {
                  "type": "field",
                  "required": false,
                  "read_only": false,
                  "label": "Transaction de cr\u00e9dit"
              },
              "transactions": {
                  "type": "field",
                  "required": true,
                  "read_only": false,
                  "label": "Transactions d'adh\u00e9sion"
              }
          }
      }
  }

Filtres Django
~~~~~~~~~~~~~~

* ``user``
* ``user__last_name``
* ``user__first_name``
* ``user__email``
* ``user__note__alias__name``
* ``user__note__alias__normalized_name``
* ``transactions``
* ``credit_transaction``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``user__last_name`` (expression régulière)
* ``user__first_name`` (expression régulière)
* ``user__email`` (expression régulière)
* ``user__note__alias__name`` (expression régulière)
* ``user__note__alias__normalized_name`` (expression régulière)

