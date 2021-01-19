API Logs
========

Journal de modification
-----------------------

**Chemin :** `/api/logs/ <https://note.crans.org/api/logs/>`_

Options
~~~~~~~

.. code:: json

  {
      "name": "Changelog List",
      "description": "REST API View set.\nThe djangorestframework plugin will get all `Changelog` objects, serialize it to JSON with the given serializer,\nthen render it on /api/logs/",
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
* ``action``
* ``instance_pk``
* ``user``
* ``ip``

Tris possible
~~~~~~~~~~~~~

* ``timestamp``
* ``id``

