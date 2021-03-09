OAuth2
======

L'authentification `OAuth2 <https://fr.wikipedia.org/wiki/OAuth>`_ est supportée par la
Note Kfet. Elle offre l'avantage non seulement d'identifier les utilisateurs, mais aussi
de transmettre des informations à un service tiers tels que des informations personnelles,
le solde de la note ou encore les adhésions de l'utilisateur, en l'avertissant sur
quelles données sont effectivement collectées.

.. danger::
   L'implémentation actuelle ne permet pas de choisir quels droits on offre. Se connecter
   par OAuth2 offre actuellement exactement les mêmes permissions que l'on n'aurait
   normalement, avec le masque le plus haut, y compris en écriture.

   Faites alors très attention lorsque vous vous connectez à un service tiers via OAuth2,
   et contrôlez bien exactement ce que l'application fait de vos données, à savoir si
   elle ignore bien tout ce dont elle n'a pas besoin.

   À l'avenir, la fenêtre d'authentification pourra vous indiquer clairement quels
   paramètres sont collectés.

Configuration du serveur
------------------------

On utilise ``django-oauth-toolkit``, qui peut être installé grâce à PIP ou bien via APT,
via le paquet ``python3-django-oauth-toolkit``.

On commence par ajouter ``oauth2_provider`` aux applications Django installées. On
n'oublie pas ni d'appliquer les migrations (``./manage.py migrate``) ni de collecter
les fichiers statiques (``./manage.py collectstatic``).

On souhaite que l'API gérée par ``django-rest-framework`` puisse être accessible via
l'authentification OAuth2. On adapte alors la configuration pour permettre cela :

.. code:: python

   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.SessionAuthentication',
           'rest_framework.authentication.TokenAuthentication',
           'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
           ...
       ],
       ...
   }

On ajoute les routes dans ``urls.py`` :

.. code:: python

   urlpatterns.append(
        path('o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
    )

L'OAuth2 est désormais prêt à être utilisé.


Configuration client
--------------------

Contrairement au `CAS <cas>`_, n'importe qui peut en théorie créer une application OAuth2.
En théorie, car pour l'instant les permissions ne leur permettent pas.

Pour créer une application, il faut se rendre à la page
`/o/applications/ <https://note.crans.org/o/applications/>`_. Dans ``client type``,
rentrez ``public`` (ou ``confidential`` selon vos choix), et vous rentrerez
généralement ``authorization-code`` dans ``Authorization Grant Type``.
Le champ ``Redirect Uris`` contient une liste d'adresses URL autorisées pour des
redirections post-connexion.

Il vous suffit de donner à votre application :

* L'identifiant client (client-ID)
* La clé secrète
* Les scopes : sous-ensemble de ``[read, write]`` (ignoré pour l'instant, cf premier paragraphe)
* L'URL d'autorisation : `<https://note.crans.org/o/authorize/>`_
* L'URL d'obtention de jeton : `<https://note.crans.org/o/token/>`_
* L'URL de récupération des informations de l'utilisateur : `<https://note.crans.org/api/me/>`_

N'hésitez pas à consulter la page `<https://note.crans.org/api/me/>`_ pour s'imprégner
du format renvoyé.

Avec Django-allauth
###################

Si vous utilisez Django-allauth pour votre propre application, vous pouvez utiliser
le module pré-configuré disponible ici :
`<https://gitlab.crans.org/bde/allauth-note-kfet>`_. Pour l'installer, vous
pouvez simplement faire :

.. code:: bash

   $ pip3 install git+https://gitlab.crans.org/bde/allauth-note-kfet.git

L'installation du module se fera automatiquement.

Il vous suffit ensuite d'inclure l'application ``allauth_note_kfet`` à vos applications
installées (sur votre propre client), puis de bien ajouter l'application sociale :

.. code:: python

   SOCIALACCOUNT_PROVIDERS = {
       'notekfet': {
           # 'DOMAIN': 'note.crans.org',
       },
       ...
   }

Le paramètre ``DOMAIN`` permet de changer d'instance de Note Kfet. Par défaut, il
se connectera à ``note.crans.org`` si vous ne renseignez rien.

En créant l'application sur la note, vous pouvez renseigner
``https://monsite.example.com/accounts/notekfet/login/callback/`` en URL de redirection,
à adapter selon votre configuration.

Vous devrez ensuite enregistrer l'application sociale dans la base de données.
Vous pouvez passer par Django-admin, mais cela peut nécessiter d'avoir déjà un compte,
alors autant le faire via un shell python :

.. code:: python

   from allauth.socialaccount.models import SocialApp
   SocialApp.objects.create(
           name="Note Kfet",
           provider="notekfet",
           client_id="VOTRECLIENTID",
           secret="VOTRESECRET",
           key="",
   )

Si vous avez bien configuré ``django-allauth``, vous êtes désormais prêts par à vous
connecter via la note :) Par défaut, nom, prénom, pseudo et adresse e-mail sont
récupérés. Les autres données sont stockées mais inutilisées.
