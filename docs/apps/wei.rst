WEI
===

Cette application gère toute la phase d'inscription au WEI.

Modèles
-------

WEIClub
~~~~~~~

Le modèle ``WEIClub`` hérite de ``Club`` et contient toutes les informations d'un WEI.

* ``year`` : ``PositiveIntegerField`` unique, année du WEI.
* ``date_start`` : ``DateField``, date de début du WEI.
* ``date_end`` : ``DateField``, date de fin du WEI.

Champs hérités de ``Club`` de l'application ``member`` : 

* ``parent_club`` : ``ForeignKey(Club)``. Ce champ vaut toujours ``Kfet`` dans le cas d'un WEI : on doit être membre du
  club Kfet pour participer au WEI.
* ``email`` : ``EmailField``, adresse e-mail sur laquelle contacter les gérants du WEI.
* ``membership_start`` : ``DateField``, date à partir de laquelle il est possible de s'inscrire au WEI.
* ``membership_end`` : ``DateField``, date de fin d'adhésion possible au WEI.
* ``membership_duration`` : ``PositiveIntegerField``, inutilisé dans le cas d'un WEI, vaut ``None``.
* ``membership_fee_paid`` : ``PositiveIntegerField``, montant de la cotisation (en centimes) pour qu'un élève normalien
  (donc rémunéré) puisse adhérer.
* ``membership_fee_unpaid`` : ``PositiveIntegerField``, montant de la cotisation (en centimes) pour qu'un étudiant
  normalien (donc non rémunéré) puisse adhérer.
* ``name`` : ``CharField``, nom du WEI.
* ``require_memberships`` : ``BooleanField``, vaut toujours ``True`` pour le WEI.

Bus
~~~

Contient les informations sur un bus allant au WEI.

* ``wei`` : ``ForeignKey(WEIClub)``, WEI auquel ce bus est rattaché.
* ``name`` : ``CharField``, nom du bus. Le champ est unique pour le WEI attaché.
* ``description`` : ``TextField``, description textuelle de l'ambiance du bus.
* ``information_json`` : ``TextField``, diverses informations non publiques qui permettent d'indiquer divers paramètres
  pouvant varier selon les années permettant l'attribution des bus aux 1A.

Il est souhaitable de créer chaque année un bus "Staff" (non accessible aux 1A bien évidemment) pour les GC WEI qui ne
monteraient pas dans un bus.

BusTeam
~~~~~~~

Contient les informations d'une équipe WEI.

* ``wei`` : ``ForeignKey(WEIClub)``, WEI auquel cette équipe est rattachée.
* ``name`` : ``CharField``, nom de l'équipe.
* ``color`` : ``PositiveIntegerField``, entier entre 0 et 16777215 = 0xFFFFFF représentant la couleur du T-Shirt.
  La donnée se rentre en hexadécimal via un sélecteur de couleur. Cette information est purement cosmétique et n'est
  utilisée nulle part.
* ``description`` : ``TextField``, description de l'équipe.

WEIRole
~~~~~~~

Ce modèle hérité de  ``Role``, ne contient qu'un champ ``name`` (``CharField``), le nom du rôle. Ce modèle ne permet
que de dissocier les rôles propres au WEI des rôles s'appliquant pour n'importe quel club.

WEIRegistration
~~~~~~~~~~~~~~~

Inscription au WEI, contenant les informations avant validation. Ce modèle est créé dès lors que quelqu'un se pré-inscrit au WEI.

* ``user`` : ``ForeignKey(User)``, utilisateur qui s'est pré-inscrit. Ce champ est unique avec ``wei``.
* ``wei`` : ``ForeignKey(WEIClub)``, le WEI auquel l'utilisateur s'est pré-inscrit. Ce champ est unique avec ``user``.
* ``soge_credit`` : ``BooleanField``, indique si l'utilisateur a déclaré vouloir ouvrir un compte à la Société générale.
* ``caution_check`` : ``BooleanField``, indique si l'utilisateur (en 2ème année ou plus) a bien remis son chèque de
  caution auprès de la trésorerie.
* ``birth_date`` : ``DateField``, date de naissance de l'utilisateur.
* ``gender`` : ``CharField`` parmi ``male`` (Homme), ``female`` (Femme), ``non binary`` (Non binaire), genre de la personne.
* ``health_issues`` : ``TextField``, problèmes de santé déclarés par l'utilisateur.
* ``emergency_contact_name`` : ``CharField``, nom du contact en cas d'urgence.
* ``emergency_contact_phone`` : ``CharField``, numéro de téléphone du contact en cas d'urgence.
* ``ml_events_registration`` : ``BooleanField``, déclare si l'utilisateur veut s'inscrire à la liste de diffusion des
  événements du BDE (1A uniquement)
* ``ml_art_registration`` : ``BooleanField``, déclare si l'utilisateur veut s'inscrire à la liste de diffusion des
  actualités du BDA (1A uniquement)
* ``ml_sport_registration`` : ``BooleanField``, déclare si l'utilisateur veut s'inscrire à la liste de diffusion des
  actualités du BDS (1A uniquement)
* ``first_year`` : ``BooleanField``, indique si l'inscription est d'un 1A ou non. Non modifiable par n'importe qui.
* ``information_json`` : ``TextField`` non modifiable manuellement par n'importe qui stockant les informations du
  questionnaire d'inscription au WEI pour les 1A, et stocke les demandes faites par un 2A+ concerant bus, équipes et rôles.
  On utilise un ``TextField`` contenant des données au format JSON pour permettre de la modularité au fil des années,
  sans avoir à tout casser à chaque fois.

WEIMembership
~~~~~~~~~~~~~

Ce modèle hérite de ``Membership`` et contient les informations d'une adhésion au WEI.

* ``bus`` : ``ForeignKey(Bus)``, bus dans lequel se trouve l'utilisateur.
* ``team`` : ``ForeignKey(BusTeam)`` pouvant être nulle (pour les chefs de bus et électrons libres), équipe dans laquelle
  se trouve l'utilisateur.
* ``registration`` : ``OneToOneField(WEIRegistration)``, informations de la pré-inscription.

Champs hérités du modèle ``Membership`` :

* ``club`` : ``ForeignKey(Club)``, club lié à l'adhésion. Doit être un ``WEIClub``.
* ``user`` : ``ForeignKey(User)``, utilisateur adhéré.
* ``date_start`` : ``DateField``, date de début d'adhésion.
* ``date_end`` : ``DateField``, date de fin d'adhésion.
* ``fee`` : ``PositiveIntegerField``, montant de la cotisation payée.
* ``roles`` : ``ManyToManyField(Role)``, liste des rôles endossés par l'adhérent. Les rôles doivent être des ``WEIRole``.

Graphe des modèles
~~~~~~~~~~~~~~~~~~

Pour une meilleure compréhension, le graphe des modèles de l'application ``member`` ont été ajoutés au schéma.

.. image:: /_static/img/graphs/wei.svg
   :alt: Graphe des modèles de l'application WEI

Fonctionnement
--------------

Création d'un WEI
~~~~~~~~~~~~~~~~~

Seul un respo info peut créer un WEI. Pour cela, se rendre dans l'onglet WEI, puis "Liste des WEI" et enfin
"Créer un WEI". Diverses informations sont demandées, comme le nom du WEI, l'adresse mail de contact, l'année du WEI
(doit être unique), les dates de début et de fin, et les dates pendant lesquelles les utilisateurs peuvent s'inscrire.

Don des droits à un GC WEI
~~~~~~~~~~~~~~~~~~~~~~~~~~

Le GC WEI peut gérer tout ce qui a un rapport avec le WEI. Il ne peut cependant pas créer le WEI, ce privilège est
réservé au respo info. Pour avoir ses droits, le GC WEI doit s'inscrire au WEI avec le rôle GC WEI, et donc payer
en premier sa cotisation. C'est donc au respo info de créer l'adhésion du GC WEI. Voir ci-dessous pour l'inscription au WEI.

S'inscrire au WEI
~~~~~~~~~~~~~~~~~

N'importe quel utilisateur peut s'auto-inscrire au WEI, lorsque les dates d'adhésion le permettent. Ceux qui se sont
déjà inscrits peuvent également inscrire un 1A. Seuls les GC WEI et les respo info peuvent inscrire un autre 2A+.

À tout moment, tant que le WEI n'est pas passé, l'inscription peut être modifiée, même après validation.

Inscription d'un 2A+
^^^^^^^^^^^^^^^^^^^^

Comme indiqué, les 2A+ sont assez autonomes dans leur inscription au WEI. Ils remplissent le questionnaire et sont
ensuite pré-inscrits. Le questionnaire se compose de plusieurs champs (voir WEIRegistration) :

* Est-ce que l'utilisateur a déclaré avoir ouvert un compte à la Société générale ? (Option disponible uniquemement
  si cela n'a pas été fait une année avant)
* Date de naissance
* Genre (Homme/Femme/Non-binaire)
* Problèmes de santé
* Nom du contact en cas d'urgence
* Numéro du contact en cas d'urgence
* Bus préférés (choix multiple, utile pour les électrons libres)
* Équipes préférées (choix multiple éventuellement vide, vide pour les chefs de bus/staff)
* Rôles souhaités

Les trois derniers champs n'ont aucun caractère définitif et sont simplement là en suggestion pour le GC WEI qui
validera l'inscription. C'est utile si on hésite entre plusieurs bus.

L'inscription est ensuite créée, le GC WEI devra ensuite la valider (voir plus bas).

Inscription d'un 1A
^^^^^^^^^^^^^^^^^^^

N'importe quelle personne déjà inscrite au WEI peut inscrire un 1A. Le formulaire 1A est assez peu différent du formulaire 2A+ :

* Est-ce que l'utilisateur a déclaré avoir ouvert un compte à la Société générale ?
* Date de naissance
* Genre (Homme/Femme/Non-binaire)
* Problèmes de santé
* Nom du contact en cas d'urgence
* Numéro du contact en cas d'urgence
* S'inscrire à la ML événements
* S'inscrire à la ML BDA
* S'inscrire à la ML BDS

Le 1A ne peut donc pas choisir de son bus et de son équipe, et peut s'inscrire aux listes de diffusion.
Il y a néanmoins une différence majeure : une fois le formulaire rempli, un questionnaire se lance.
Ce questionnaire peut varier au fil des années (voir section Questionnaire), et contient divers formulaires de collecte
de données qui serviront à déterminer quel est le meilleur bus pour ce nouvel utilisateur.

Questionnaire 1A
^^^^^^^^^^^^^^^^

Le questionnaire 1A permet de poser des questions aux 1A lors de leur inscription au WEI afin de déterminer quel serait
le meilleur bus pour eux. Un algorithme attribue ensuite à chaque 1A le bus sélectionné.

Afin de permettre de la modularité et de s'adapter aux changements au fil des années, il n'y a pas de modèle dédié au
sondage. On sauvegarde alors les données du sondage sous la forme d'un dictionnaire enregistré au format JSON
dans le champ ``information_json`` du modèle ``WEIRegistration``. Ce champ est modifiable manuellement uniquement par
les respos info et les GC WEI.

Je veux changer d'algorithme de répartition, que faire ?
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Cette section est plus technique et s'adresse surtout aux respos info en cours de mandat.

Première règle : on ne supprime rien (sauf si vraiment c'est du mauvais boulot). En prenant exemple sur des fichiers déjà existant tels que ``apps/wei/forms/surveys/wei2020.py``, créer un nouveau fichier ``apps/wei/forms/surveys/wei20XY.py``. Ce fichier doit inclure les éléments suivants :

WEISurvey
"""""""""

Une classe héritant de ``wei.forms.surveys.base.WEISurvey``, comportant les éléments suivants :

* Une fonction ``get_year(cls)`` indiquant l'année du WEI liée au sondage
* Une fonction ``get_survey_information_class(cls)`` indiquant la classe héritant de
  ``wei.forms.surveys.base.WEISurveyInformation`` contenant les données du sondage (voir plus bas)
* Une fonction ``get_algorithm_class(cls)`` indiquant la classe héritant de
  ``wei.forms.surveys.base.WEISurveyAlgorithm`` contenant l'algorithme de répartition (voir plus bas)
* Une fonction ``get_form_class(self)`` qui indique la classe du formulaire Django à remplir. Cette classe peut dépendre
  de l'état actuel du sondage.
* Une fonction ``update_form(self, form)``, optionnelle, appelée lorsqu'un formulaire dont la classe est spécifiée via
  la fonction ``get_form_class``, et permet d'opérer sur le formulaire si besoin.
* Une fonction ``form_valid(self, form)`` qui indique quoi faire lorsque le formulaire est rempli. Cette fonction peut
  bien sûr dépendre de l'état actuel du sondage.
* Une fonction ``is_complete(self)`` devant renvoyer un booléen indiquant si le sondage est complet ou non.

Naturellement, il est implicite qu'une fonction ayant pour premier argument ``cls`` doit être annotée par ``@classmethod``.
Nativement, la classe ``WEISurvey`` comprend les informations suivantes :

* ``registration``, le modèle ``WEIRegistration`` de l'utilisateur qui remplit le questionnaire
* ``information``, instance de ``WEISurveyInformation``, contient les données du questionnaire en cours de remplissage.
* ``get_wei(cls)``, renvoie le WEI correspondant à l'année du sondage.
* ``save(self)``, enregistre les informations du sondage dans l'objet ``registration`` associé, qui est ensuite
  enregistré en base de données.
* ``select_bus(self, bus)``, choisit le bus ``bus`` comme bus préféré. Cela à pour effet de remplir les champs
  ``selected_bus_pk`` et ``selected_bus_name`` par les identifiant et nom du bus, et ``valid`` à ``True``.

Pour information, ``WEISurvey.__init__`` prend comme paramètre l'inscription ``registration``, et récupère les
informations du sondage converties en dictionnaire Python puis en objet ``WEISurveyInformation``.

WEISurveyInformation
""""""""""""""""""""

Une classe héritant de ``wei.forms.surveys.base.WEISurveyInformation``, comportant les informations brutes du sondage.
Le champ ``information_json`` de ``WEIRegistration`` est traduit en dictionnaire Python depuis JSON, puis les différents
champs de WEISurveyInformation sont mis à jour depuis ce dictionnaire. Il n'y a rien de supplémentaire à ajouter, tout
est déjà géré.

Ainsi, plutôt que de modifier laborieusement le champ JSON, préférez utiliser cette classe. Attention : pour des soucis
de traduction facile, merci de n'utiliser que des objets primitifs (nombres, chaînes de caractère, booléens, listes,
dictionnaires simples). Les instances de modèle sont à proscrire, préférez stocker l'identifiant et créer une fonction
qui récupère l'instance à partir de l'identifiant.

Attention, 3 noms sont réservés : ``selected_bus_pk``, ``selected_bus_name`` et ``valid``, qui représentent la sortie
de l'algorithme de répartition.

À noter que l'interface de validation des inscriptions affiche les données brutes du sondage.

WEIBusInformation
"""""""""""""""""

Une classe héritant de ``wei.forms.surveys.base.WEIBusInformation``, qui contient les informations sur un bus,
de la même manière que ``WEISurveyInformation`` contient les informations d'un sondage. Le fonctionnement est le même :
on récupère le champ ``information_json`` du modèle ``Bus`` qu'on convertit en dictionnaire puis en objet Python.
Cet objet est en lecture uniquement, on modifie à la main les paramètres d'un bus.

Le champ ``bus`` est fourni.

WEISurveyAlgorithm
""""""""""""""""""

Une classe héritant de ``wei.forms.surveys.base.WEISurveyAlgorithm``, qui contient 3 fonctions :

* ``get_survey_class(cls)``, qui renvoie la classe du ``WEISurvey`` associée à l'algorithme.
* ``get_bus_information_class(cls)`` qui renvoie la classe du ``WEIBusInformation`` décrivant les informations d'
* ``run_algorithm(self)``, la fonction importante. Cette fonction n'est supposée n'être exécutée qu'une seule fois
  par WEI, et a pour cahier des charges de prendre chaque sondage d'un 1A et d'appeler la fonction ``WEISurvey.select_bus(bus)``,
  en décidant convenablement de quel bus le membre doit prendre. C'est bien sûr la fonction la plus complexe à mettre en oeuvre.
  Tout est permis tant qu'à la fin tout le monde a bien son bus.

Trois fonctions sont implémentées nativement :

* ``get_registrations(cls)``, renvoie un ``QuerySSet`` vers l'ensemble des inscriptions au WEI concerné des 1A.
* ``get_buses(cls)``, renvoie l'ensemble des bus du WEI concerné.
* ``get_bus_information(cls, bus)``, renvoie l'objet ``WEIBusInformation`` instancié avec les informations fournies
  par le champ ``information_json`` de ``bus``.


La dernière chose à faire est dans le fichier ``apps/wei/forms/surveys/__init__.py``, où la classe ``CurrentSurvey``
est à mettre à jour. Il n'y a rien d'autre à changer, tout le reste est normalement géré pour qu'il n'y ait pas nécessité
d'y toucher.

Le lancement de l'algorithme se fait en ligne de commande, via la commande ``python manage.py wei_algorithm``. Elle a
pour unique effet d'appeler la fonction ``run_algorithm`` décrite plus tôt. Une fois cela fait, vous aurez noté qu'il
n'a pas été évoqué d'adhésion. L'adhésion est ensuite manuelle, l'algorithme ne fournit qu'une suggestion.

Cette structure, complexe mais raisonnable, permet de gérer plus ou moins proprement la répartition des 1A,
en limitant très fortement le hard code. Ami nouveau développeur, merci de bien penser à la propreté du code :)
En particulier, on évitera de mentionner dans le code le nom des bus, et profiter du champ ``information_json``
présent dans le modèle ``Bus``.

Valider les inscriptions
~~~~~~~~~~~~~~~~~~~~~~~~

Cette partie est moins technique.

Une fois la pré-inscription faite, elle doit être validée par le BDE, afin de procéder au paiement. Le GC WEI a accès à
la liste des inscriptions non validées, soit sur la page de détails du WEI, soit sur un tableau plus large avec filtre.
Une inscription non validée peut soit être validée, soit supprimée (la suppression est irréversible).

Lorsque le GC WEI veut valider une inscription, il a accès au récapitulatif de l'inscription ainsi qu'aux informations
personnelles de l'utilisateur. Il lui est proposé de les modifier si besoin (du moins les informations liées au WEI,
pas les informations personnelles). Il a enfin accès aux résultats du sondage et la sortie de l'algorithme s'il s'agit
d'un 1A, aux préférences d'un 2A+. Avant de valider, le GC WEI doit sélectionner un bus, éventuellement une équipe
et un rôle. Si c'est un 1A et que l'algorithme a tourné, ou si c'est un 2A+ qui n'a fait qu'un seul choix de bus,
d'équipe, de rôles, les champs sont automatiquement pré-remplis.

Quelques restrictions cependant :

* Si c'est un 2A+, le chèque de caution doit être déclaré déposé
* Si l'inscription se fait via la Société générale, un message expliquant la situation apparaît : la transaction de
  paiement sera créée mais invalidée, les trésoriers devront confirmer plus tard sur leur interface que le compte
  à la Société générale a bien été créé avant de valider la transaction (voir `Trésorerie <treasury>`_ section
  Crédit de la Société générale).
* Dans le cas contraire, l'utilisateur doit avoir le solde nécessaire sur sa note avant de pouvoir adhérer.
* L'utilisateur doit enfin être membre du club Kfet. Un lien est présent pour le faire adhérer ou réadhérer selon le cas.

Si tout est bon, le GC WEI peut valider. L'utilisateur a bien payé son WEI, et son interface est un peu plus grande.
Il peut toujours changer ses paramètres au besoin. Un 1A ne voit rien de plus avant la fin du WEI.

Un adhérent WEI non 1A a accès à la liste des bus, des équipes et de leur descriptions. Les chefs de bus peuvent gérer
les bus et leurs équipes. Les chefs d'équipe peuvent gérer leurs équipes. Cela inclut avoir accès à la liste des membres
de ce bus / de cette équipe.

Un export au format PDF de la liste des membres *visibles* est disponible pour chacun.

Bon WEI à tous !
