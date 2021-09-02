OAuth2
======

L'authentification `OAuth2 <https://fr.wikipedia.org/wiki/OAuth>`_ est supportée par la
Note Kfet. Elle offre l'avantage non seulement d'identifier les utilisateurs, mais aussi
de transmettre des informations à un service tiers tels que des informations personnelles,
le solde de la note ou encore les adhésions de l'utilisateur, en l'avertissant sur
quelles données sont effectivement collectées. Ainsi, il est possible de développer des
appplications tierces qui peuvent se baser sur les données de la Note Kfet ou encore
faire des transactions.


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

On a ensuite besoin de définir nos propres scopes afin d'avoir des permissions fines :

.. code:: python

   OAUTH2_PROVIDER = {
       'SCOPES_BACKEND_CLASS': 'permission.scopes.PermissionScopes',
   }

On ajoute enfin les routes dans ``urls.py`` :

.. code:: python

   urlpatterns.append(
        path('o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
    )

L'OAuth2 est désormais prêt à être utilisé.


Configuration client
--------------------

Contrairement au `CAS <cas>`_, n'importe qui peut créer une application OAuth2.

Pour créer une application, il faut se rendre à la page
`/o/applications/ <https://note.crans.org/o/applications/>`_. Dans ``client type``,
rentrez ``public`` (ou ``confidential`` selon vos choix), et vous rentrerez
généralement ``authorization-code`` dans ``Authorization Grant Type``.
Le champ ``Redirect Uris`` contient une liste d'adresses URL autorisées pour des
redirections post-connexion.

Il vous suffit de donner à votre application :

* L'identifiant client (client-ID)
* La clé secrète
* Les scopes, qui peuvent être récupérées sur cette page : `<https://note.crans.org/permission/scopes/>`_
* L'URL d'autorisation : `<https://note.crans.org/o/authorize/>`_
* L'URL d'obtention de jeton : `<https://note.crans.org/o/token/>`_
* Si besoin, l'URL de récupération des informations de l'utilisateur : `<https://note.crans.org/api/me/>`_

N'hésitez pas à consulter la page `<https://note.crans.org/api/me/>`_ pour s'imprégner
du format renvoyé.

.. warning::

   Un petit mot sur les scopes : tel qu'implémenté, une scope est une permission unitaire
   (telle que décrite dans le modèle ``Permission``) associée à un club. Ainsi, un jeton
   a accès à une scope si et seulement si le/la propriétaire du jeton dispose d'une adhésion
   courante dans le club lié à la scope qui lui octroie cette permission.

   Par exemple, un jeton pourra avoir accès à la permission de créer des transactions en lien
   avec un club si et seulement si le propriétaire du jeton est trésorier du club.

   La vérification des droits du propriétaire est faite systématiquement, afin de ne pas
   faire confiance au jeton en cas de droits révoqués à son propriétaire.

   Vous pouvez donc contrôler le plus finement possible les permissions octroyées à vos
   jetons.

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


Application personnalisée
#########################

Ce modèle vous permet de créer vos propres applications à interfacer avec la Note Kfet.

Commencez par créer une application : `<https://note.crans.org/o/applications/register>`_.
Dans ``Client type``, choisissez ``Confidential`` si des informations confidentielles sont
amenées à transiter, sinon ``public``. Choisissez ``Authorization code`` dans
``Authorization grant type``.

Dans ``Redirect uris``, vous devez insérer l'ensemble des URL autorisées à être redirigées
à la suite d'une autorisation OAuth2. La première URL entrée sera l'URL par défaut dans le
cas où elle n'est pas explicitement indiquée lors de l'autorisation.

.. note::

   À des fins de tests, il est possible de laisser `<http://localhost/>`_ pour faire des
   appels à la main en récupérant le jeton d'autorisation.

Lorsqu'un client veut s'authentifier via la Note Kfet, il va devoir accéder à une page
d'authentification. La page d'autorisation est `<https://note.crans.org/o/authorize/>`_,
c'est sur cette page qu'il faut rediriger les utilisateurs. Il faut mettre en paramètre GET :

* ``client_id`` : l'identifiant client de l'application (public) ;
* ``response_type`` : mettre ``code`` ;
* ``scope`` : l'ensemble des scopes demandés, séparés par des espaces. Ces scopes peuvent
  être récupérés sur la page `<https://note.crans.org/permission/scopes/>`_.
* ``redirect_uri`` : l'URL sur laquelle rediriger qui récupérera le code d'accès. Doit être
  autorisée par l'application. À des fins de test, peut être `<http://localhost/>`_.
* ``state`` : optionnel, peut être utilisé pour permettre au client de détecter des requêtes
  provenant d'autres sites.

Sur cette page, les permissions demandées seront listées, et l'utilisateur aura le choix
d'accepter ou non. Dans les deux cas, l'utilisateur sera redirigée vers ``redirect_uri``,
avec pour paramètre GET soit le message d'erreur, soit un paramètre ``code`` correspondant
au code d'autorisation.

Une fois ce code d'autorisation récupéré, il faut désormais récupérer le jeton d'accès.
Il faut pour cela aller sur l'URL `<https://note.crans.org/o/token/>`_, effectuer une
requête POST avec pour arguments :

* ``client_id`` ;
* ``client_secret`` ;
* ``grant_type`` : mettre ``authorization_code`` ;
* ``code`` : le code généré.

À noter que le code fourni n'est disponible que pendant quelques secondes.

À des fins de tests, on peut envoyer la requête avec ``curl`` :

.. code:: bash

   curl -X POST https://note.crans.org/o/token/ -d "client_id=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&client_secret=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&grant_type=authorization_code&code=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

Le serveur renverra si tout se passe bien une réponse JSON :

.. code:: json

   {
       "access_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
       "expires_in": 36000,
       "token_type": "Bearer",
       "scope": "1_1 1_2",
       "refresh_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   }

On note donc 2 jetons différents : un d'accès et un de rafraîchissement. Le jeton d'accès
est celui qui sera donné à l'API pour s'authentifier, et qui expire au bout de quelques
heures.

Il suffit désormais d'ajouter l'en-tête ``Authorization: Bearer ACCESS_TOKEN`` pour se
connecter à la note grâce à ce jeton d'accès.

Pour tester :

.. code:: bash

   curl https://note.crans.org/api/me -H "Authorization: Bearer XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

En cas d'expiration de ce jeton d'accès, il est possible de le renouveler grâce au jeton
de rafraichissement à usage unique. Il suffit pour cela de refaire une requête sur la page
`<https://note.crans.org/o/token/>`_ avec pour paramètres :

* ``client_id`` ;
* ``client_secret`` ;
* ``grant_type`` : mettre ``refresh_token`` ;
* ``refresh_token`` : le jeton de rafraîchissement.

Le serveur vous fournira alors une nouvelle paire de jetons, comme précédemment.
À noter qu'un jeton de rafraîchissement est à usage unique.

N'hésitez pas à vous renseigner sur OAuth2 pour plus d'informations.
