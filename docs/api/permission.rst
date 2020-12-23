API Permissions
===============

Permission
----------

**Chemin :** `/api/permission/permission/ <https://note.crans.org/api/permission/permission/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Permission List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Permission` objects, serialize it to JSON with the given serializer,\nthen render it on /api/permission/permission/",
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

* ``model``
* ``type``
* ``query``
* ``mask``
* ``field``
* ``permanent``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``model__name`` (expression régulière)
* ``query`` (expression régulière)
* ``description`` (expression régulière)

Permissions par rôles
---------------------

**Chemin :** `/api/permission/roles/ <https://note.crans.org/api/permission/roles/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Role List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `RolePermission` objects, serialize it to JSON with the given serializer\nthen render it on /api/permission/roles/",
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

* ``name``
* ``permissions``
* ``for_club``
* ``memberships__user``

Filtres de recherche
~~~~~~~~~~~~~~~~~~~~

* ``name`` (expression régulière)
* ``for_club__name`` (expression régulière)

