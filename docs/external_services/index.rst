Applications externes
=====================

.. toctree::
   :maxdepth: 2
   :caption: Applications externes

   cas
   oauth2

.. warning::
   L'utilisation de la note par des services externes est actuellement en beta. Il est
   fort à parier que cette utilisation sera revue et améliorée à l'avenir.

Puisque la Note Kfet recense tous les comptes des adhérents BDE, les clubs ont alors
la possibilité de développer leurs propres applications et de les interfacer avec la
note. De cette façon, chaque application peut authentifier ses utilisateurs via la note,
et récupérer leurs adhésion, leur nom de note afin d'éventuellement faire des transferts
via l'API.

Deux protocoles d'authentification sont implémentées :

 * `CAS <cas>`_
 * `OAuth2 <oauth2>`_

À ce jour, il n'y a pas encore d'exemple d'utilisation d'application qui utilise ce
mécanisme, mais on peut imaginer par exemple que la Mediatek ou l'AMAP implémentent
ces protocoles pour récupérer leurs adhérents.
