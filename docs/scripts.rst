Les scripts de la Note Kfet 2020
================================

Django permet la création de scripts permettant l'interaction en ligne de commande
avec le site. Les scripts sont gérés dans un projet à part :
`nk20-scripts <https://gitlab.crans.org/bde/nk20-scripts>`_.

Il s'agit d'un module Python à part contenant tous les scripts interagissant avec la note.
Pour l'installer, il suffit d'importer le sous module (``git submodule init apps/scripts``)
ou bien d'avoir ajouté l'option ``--recursive`` lorsque le dépôt a été cloné. Il faut
ensuite ajouter le module au tableau ``INSTALLED_APPS`` dans les paramètres.


Scripts Python
##############

Structure d'un script
---------------------

Un script est un fichier Python placé dans ``apps/scripts/management/commands``. Le nom
de fichier sans l'extension ``.py`` caractérise le nom du script. On supposera dans la suite
qu'on aura créé le script ``toto.py``. Pour lancer le script, il suffira de lancer
``./manage.py toto``. Django se charge de trouver l'emplacement du script. Un simple
``./manage.py`` affichera par ailleurs la liste des scripts par application.

Ce fichier Python doit contenir une classe nommée ``Command`` héritant de
``django.core.management.base.BaseCommand``.

Il suffit enfin de créer une fonction ``handle(self, *args, **options) -> None``.
C'est cette fonction qui servira à l'exécution du script. ``options`` contient
l'ensemble des options transmises.

Pour gérer les options, créez une fonction ``add_arguments(self, parser)``.
``parser`` vous permet de gérer vos arguments. Plus d'informations dans la documentation
du module ``argparse`` de Python : https://docs.python.org/fr/3/library/argparse.html

.. warning::

   Bonne pratique : si votre script doit écrire sur la base de données, pensez à
   ajouter un décorateur ``@transaction.atomic`` (du module ``django.db``) sur
   votre fonction ``handle``. Cela aura pour effet de ne pas effectuer les modifications
   indiquées en cas d'erreur dans le script. Cela évite de vous retrouver avec une base
   de données dans un état instable en cas d'erreur dans le script, ou en développement
   (sur un serveur de développement bien sûr).

.. warning::

   Par défaut, chaque commande dispose d'un certain nombre d'options, dont ``--help`` qui
   affiche l'aide et les options disponibles, et ``--verbosity {0, 1, 2, 3}`` qui permet
   de contrôler la verbosité du script. Il est important d'en tenir compte, en particulier
   un niveau de verbosité nul ne devrait afficher rien d'autre que des erreurs.

Plus d'informations dans la documentation officielle :
https://docs.djangoproject.com/fr/2.2/howto/custom-management-commands/


Anonymisation de données
------------------------

Le script s'appelle ``anonymize_data``.

Ce script était utilisé lors de la beta de la Note Kfet 2020, afin d'anonymiser certaines
données personnelles et limiter le risque de fuites de données. Ainsi, les noms, prénoms,
adresses électroniques, numéros de téléphone et adresses étaient normalisées.

Ce script étant dangereux, l'option ``--force`` est requise.


Vérification de l'intégrité des données
---------------------------------------

Le script s'appelle ``check_consistency``.

Son but est de s'assurer que la somme des montants de toutes les notes vaut bien zéro,
et que pour chaque note, la somme des transactions donne bien le solde de la note.

En cas de problème, les erreurs détectées sont affichées.

Le script prend plusieurs options :

* ``--sum-all, -s`` : vérifie si la somme des notes vaut bien 0
* ``--check-all, -a`` : vérifie si le solde de toutes les notes est cohérent
* ``--check, -c`` : si l'option précédente n'est pas présente, indique les identifiants
  des notes à vérifier
* ``--fix, -f`` : Rétablit le solde des notes à la somme des transactions. À n'utiliser
  qu'après avoir identifié le problème.

Ce script est appelé tous les jours à 4h du matin avec les options ``--sum-all --check-all``,
et en cas d'erreur un mail est envoyé.


Compilation des messages JavaScript
-----------------------------------

Le script s'appelle ``compilejsmessages``.

Django gère nativement la traduction des chaînes de caractères, avec notamment les scripts
``makemessages`` et ``compilemessages``. Django permet également de gérer la traduction
dans les fichiers statiques JavaScript, comme l'indique la documentation officielle :
https://docs.djangoproject.com/fr/2.2/topics/i18n/translation/#internationalization-in-javascript-code

Comme l'indique cette documentation, cela revient à ajouter un fichier Javascript contenant
l'ensemble des traductions et le navigateur s'occupe de récupérer les bonnes traductions.

Cependant, la façon standard de gérer cela est d'avoir une vue dédiée qui générera le bon
fichier Javascript. Les traductions ne changeant pas souvent (à chaque mise à jour
uniquement), il n'est pas essentiel de les recompiler à chaque chargement de page.

Le protocole choisi est donc de générer des fichiers statiques, qui seront donc directement
servis par Nginx (et éventuellement mis en cache par le client) et non recalculés à chaque
fois. On optimise donc les requêtes.

Pour rappel, pour générer les fichiers de traduction Javascript :

.. code:: bash

   ./manage.py makemessages -i env -e js -d djangojs

Et on peut donc appeler ce script ``compilejsmessages`` pour créer les fichiers Javascript
correspondant et le placer dans le dossier des fichiers statiques.


Extraction des listes de diffusion
----------------------------------

Le script s'appelle ``extract_ml_registrations``.

Il a pour but d'extraire une liste d'adresses mail pour les inclure directement dans les listes
de diffusion utiles.

Il prend 2 options :

* ``--type``, qui prend en argument ``members`` (défaut), ``clubs``, ``events``, ``art``,
  ``sport``, qui permet respectivement de sortir la liste des adresses mails des adhérents
  actuels (pour la liste ``adherents.bde@lists.crans.org), des clubs (pour
  ``clubs@lists.crans.org``), des personnes à abonner à ``evenements@lists.crans.org``,
  à ``all.bda@lists.crans.org`` et enfin à ``bds@lists.crans.org``.
* ``--lang``, qui prend en argument ``fr`` ou ``en``. N'est utile que pour la ML événements,
  qui a pour projet d'être disponible à la fois en anglais et en français.

Le script sort sur la sortie standard la liste des adresses mails à inscrire.

Attention : il y a parfois certains cas particuliers à prendre en compte, il n'est
malheureusement pas aussi simple que de simplement supposer que ces listes sont exhaustives.

À terme, il pourrait être envisageable de synchroniser automatiquement les listes avec la note.


Suppression d'un utilisateur
----------------------------

Le script s'appelle ``force_delete_user``.

.. caution::

   Ce script est dangereux. À n'utiliser qu'avec de très grosses pincettes si vous savez
   ce que vous faites. Seul cas d'usage pour l'instant recensé : supprimer des comptes en
   double qui se sont malencontreusement retrouvés validés pour raison de Sogé et de mauvaise
   communication au sein des trésorier⋅ère⋅s.

   Il n'est certainement pas prévu de supprimer des vrais comptes existants via ce script.
   On ne supprime pas l'historique. Si jamais quelqu'un demanderait à supprimer son compte,
   on se contente de l'anonymiser, et non de le supprimer.

Ce script est utile lorsqu'il faut supprimer un compte créer par erreur. Tant que la validation
n'est pas faite, il suffit en général de cliquer sur le bouton « Supprimer le compte » sur
l'interface de validation. Cela supprimera l'utilisateur et le profil associé, sans toucher
à une quelconque note puisqu'elle ne sera pas créée.

Ce script supprime donc un compte ainsi que toutes les données associées (note, alias,
transactions). Il n'est donc pas à prendre à la légère, et vous devez savoir ce que vous
faites.

Il prend en arguments les identifiants numériques ou un alias de la ou des personnes à
supprimer.

Sans rien ajouter, il affichera uniquement les éléments qui seront supprimés.

Avec l'option ``--force``, il commencera à créer une transaction dans la base de données
pour supprimer tout ce qu'il faut, et une validation manuelle sera requise pour confirmer
la suppression. L'option ``--doit`` évite cette confirmation manuelle.
**Vous n'avez jamais à utiliser cette option en théorie.**

À la fin du processus, un mail est envoyé aux administrateurs pour les prévenir des
élements supprimés.

Des données réelles jamais tu ne supprimeras.


Importation de la Note Kfet 2015
--------------------------------

Les scripts commençant par ``import_`` sont destinés à l'import des données depuis
la Note Kfet 2015.

.. warning::

   TODO: Pour la postérité et la conservation d'archives, documenter comment l'import
   s'est déroulé.


Ajouter un super-utilisateur
----------------------------

Le script s'appelle ``make_su``.

Il prend en argument un pseudo.

Avec l'option ``--SUPER, -S``, la personne avec ce pseudo devient super-utilisateur,
et obtiens donc les pleins pouvoirs sur la note. À ne donner qu'aux respos info.

Avec l'option ``--STAFF, -s``, la personne avec ce pseudo acquiert le statut équipe,
et obtiens l'accès à django-admin. À ne donner qu'aux respos info.


Rafraîchissement des activités
------------------------------

Le script s'appelle ``refresh_activities``.

Il a pour but de mettre à jour le Wiki du Crans automatiquement en ajoutant les
activités de la Note Kfet sur le calendrier, à savoir les pages
`<https://wiki.crans.org/VieBde/PlanningSoirees>`_ et
`<https://wiki.crans.org/VieBde/PlanningSoirees/LeCalendrier>`_.

Il prend diverses options :

* ``--human, -H`` : met à jour la version lisible de la page des activités
* ``--raw, -r`` : met à jour la version brute de la page des activités, interprétable
  par le calendrier
* ``--comment, -c`` : définit le commentaire à ajouter à la modification du wiki
* ``--stdout, -o`` : affiche la page sur la sortie standard
* ``--wiki, -w`` : applique effectivement les modifications sur le wiki

Ce script est appelé tous les jours à 5h30 avec les options
``--raw --human --comment refresh --wiki``.


Rafraîchissement des boutons mis en avant
-----------------------------------------

Le script s'appelle ``refresh_highlighted_buttons``.

Il permet d'actualiser la liste des boutons mis en avant sur la page de consommations
qui servent de raccourcis.

Ce script récupère la liste des 10 boutons les plus cliqués les 30 derniers jours et
les met en avant.


Envoi des rappels de négatif
----------------------------

Le script s'appelle ``send_mail_to_negative_balances``.

Il sert à rappeler aux adhérent⋅e⋅s et clubs en négatif qu'ils le sont, mais également
à envoyer aux trésorier⋅ère⋅s et respos info la liste des adhérent⋅e⋅s en négatif.

Il prend les options suivantes :

* ``--spam, -s`` : envoie à chaque adhérent⋅e en négatif un rappel par mail pour recharger
* ``--report, -r`` : envoie le rapport aux trésorier⋅ère⋅s et respos info
* ``--negative-amount,-n`` : définit le solde maximal en-dessous duquel les notes
  apparaitront sur le rapport / seront spammées
* ``--add-years, -y`` : ajoute également les adhérent⋅e⋅s des ``n`` dernières années

Ce script est appelé tous les mardis à 5h00 pour spammer les utilisateur⋅rice⋅s en
négatif et tous les 6 du mois pour envoyer le rapport des notes d'adhérent⋅e⋅s ou de
vieux/vieilles adhérent⋅e⋅s de moins d'un an sous -10 €.


Envoi des rapports
------------------

Le script s'appelle ``send_reports``.

Les utilisateurs ont la possibilité de recevoir sur demande un rapport à la fréquence de
leur choix (en jours) des transactions effectuées sur leur note.

Le script prend 2 options :

* ``--notes, -n`` : sélectionne les notes auxquelles envoyer un rapport. Si non spécifié,
  envoie un mail à toutes les notes demandant un rapport.
* ``--debug, -d`` : affiche les rapports dans la sortie standard sans les envoyer par mail.
  Les dates de dernier rapport ne sont pas actualisées.

Ce script est appelé tous les jours à 6h55.


Scripts bash
############

À quelques fins utiles, certains scripts bash sont également présents, dans le dossier
``scripts/shell``.


Sauvegardes de la base de données
---------------------------------

Le script ``backup_db`` permet de faire une sauvegarde de la base de données PostgreSQL
et l'envoie sur ``club-bde@zamok.crans.org``. Le script doit être lancé en tant que root.


Tabularasa
----------

Ce script n'a un intérêt qu'en développement, afin de détruire la base de données et la
recréer en appliquant les migrations et en chargeant les données initiales.
