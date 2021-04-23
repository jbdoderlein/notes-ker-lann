Service d'Authentification Centralisé (CAS)
===========================================

Un `CAS <https://fr.wikipedia.org/wiki/Central_Authentication_Service>`_ est
déployé sur la Note Kfet. Il est accessible à l'adresse `<https://note.crans.org/cas/>`_.
Il a pour but uniquement d'authentifier les utilisateurs via la note et ne communique
que peu d'informations.

Configuration
-------------

Le serveur CAS utilisé est implémenté grâce au paquet ``django-cas-server``. Il peut être
installé soit par PIP soit sur une machine Debian via
``apt install python3-django-cas-server``.

On ajoute ensuite ``cas_server`` aux applications Django installées. On n'oublie pas ni
d'appliquer les migrations (``./manage.py migrate``) ni de collecter les fichiers
statiques (``./manage.py collectstatic``).

On enregistre les routes dans ``note_kfet/urls.py`` :

.. code:: python

   urlpatterns.append(
        path('cas/', include('cas_server.urls', namespace='cas_server'))
    )

Le CAS est désormais déjà prêt à être utilisé. Toutefois, puisque l'on utilise un site
Django-admin personnalisé, on n'oublie pas d'enregistrer les pages d'administration :

.. code:: python

   if "cas_server" in settings.INSTALLED_APPS:
       from cas_server.admin import *
       from cas_server.models import *
       admin_site.register(ServicePattern, ServicePatternAdmin)
       admin_site.register(FederatedIendityProvider, FederatedIendityProviderAdmin)

Enfin, on souhaite pouvoir fournir au besoin le pseudo normalisé. Pour cela, on crée une
classe dans ``member.auth`` :

.. code:: python

   class CustomAuthUser(DjangoAuthUser):
       def attributs(self):
           d = super().attributs()
           if self.user:
               d["normalized_name"] = Alias.normalize(self.user.username)
           return d


Puis on source ce fichier dans les paramètres :

.. code:: python

   CAS_AUTH_CLASS = 'member.auth.CustomAuthUser'

Utilisation
-----------
Le service est accessible sur `<https://note.crans.org/cas/>`_. C'est ce lien qu'il faut
donner à votre application.

L'application doit néanmoins être autorisée à accéder au CAS. Pour cela, rendez-vous
dans Django-admin (`<https://note.crans.org/cas/admin/>`_), dans
``Service Central d'Authentification/Motifs de services``, ajoutez une nouvelle entrée.
Choisissez votre position favorite puis le nom de l'application.

Les champs importants sont les deux suivants :

* **Motif :** il s'agit d'une expression régulière qui doit reconnaitre le site voulu.
  Par exemple, pour autoriser Belenios (`<https://belenios.crans.org>`_), on rentrera
  le motif ``^https?://belenios\.crans\.org/.*$``.
* **Champ d'utilisateur :** C'est le pseudo que renverra le CAS. Par défaut, il s'agira
  du nom de note principal, mais il arrive parfois que certains sites supportent mal
  d'avoir des caractères UTF-8 dans le pseudo. C'est par exemple le cas de Belenios.
  On rentrera alors ``normalized_name`` dans ce champ, qui correspond à la version
  normalisée (sans accent ni espace ni aucun caractère non-ASCII) du pseudo, et qui
  suffit à identifier une personne.

On peut également utiliser le ``Single log out`` si besoin.
