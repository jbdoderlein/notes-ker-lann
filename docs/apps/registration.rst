Inscriptions
============

L'inscription a la note se fait via une application dédiée, sans toutefois avoir de modèle en base de données.

Un formulaire d'inscription est disponible sur la page ``/registration/signup``, accessible depuis n'importe qui,
authentifié ou non. Les informations suivantes sont demandées :

* Prénom
* Nom de famille
* Adresse électronique valide
* Mot de passe
* Confirmation du mot de passe
* Numéro de téléphone (optionnel)
* Département d'études
* Promotion, année d'entrée à l'ENS
* Adresse (optionnel)
* Payé (si la personne perçoit un salaire)

Le mot de passe doit vérifier des contraintes de longueur, de complexité et d'éloignement des autres informations
personnelles.

Le compte est ensuite créé, mais est inactif : la personne ne peut pas se connecter. Elle reçoit un mail lui
demandant de vérifier son adresse. Une fois le lien cliqué, l'adresse mail est validée, mais le compte reste
inactif et la connexion impossible.

Pour valider son compte, il faut se rendre à la Kfet et payer les 5 € d'adhésion BDE (ou 40 € si adhésion Kfet en plus,
15 € si on est après le 1er mars), ou bien dire qu'on a ouvert un compte à la Société générale qui paiera alors
l'adhésion. Le BDE pourra alors contrôler les informations du nouveau venu et valider son inscription.
Toutefois, même si l'inscription est validée, l'inscription restera impossible tant que l'adresse e-mail ne sera pas
validée. Le BDE peut mettre à jour l'adresse e-mail si besoin. Dès lors que l'adresse e-mail sera validée,
le compte sera enfin actif.

Pour récapituler : compte actif = adresse e-mail validée + inscription validée par le BDE.

Lors de la validation de l'inscription, le BDE peut (et doit même) faire un crédit initial sur la future note de
l'utilisateur. Il peut spécifier le type de crédit (carte bancaire/espèces/chèque/virement bancaire), le prénom,
le nom et la banque comme un crédit normal. Cependant, il peut aussi cocher une case "Société générale", si le nouveau
membre indique avoir ouvert un compte à la Société générale via le partenariat Société générale - BDE de
l'ÉNS Paris-Saclay. Dans ce cas, tous les champs sont grisés.

Une fois l'inscription validée, détail de ce qu'il se passe :

* Si crédit de la socitété générale, on mémorise que le fait que la personne ait demandé ce crédit (voir
  `Trésorerie <treasury>`_ section crédits de la société générale). Nécessairement, le club Kfet doit être rejoint.
* Sinon, on crédite la note du montant demandé par le nouveau membre (avec comme description "Crédit TYPE (Inscription)"
  où TYPE est le type de crédit), après avoir vérifié que le crédit est suffisant (on n'ouvre pas une note négative)
* On adhère la personne au BDE, l'adhésion commence aujourd'hui. Il dispose d'un unique rôle : "Adhérent",
  lui octroyant un faible nombre de permissions de base, telles que la visualisation de son compte.
* On adhère la personne au club Kfet si cela est demandé, l'adhésion commence aujourd'hui. Il dispose d'un unique rôle :
  "Adhérent Kfet", lui octroyant un nombre un peu plus conséquent de permissions basiques, telles que la possibilité de
  faire des transactions, d'accéder aux activités, au WEI, ...
* Si le nouveau membre a indiqué avoir ouvert un compte à la société générale, alors les transactions sont invalidées,
  la note n'est pas débitée (commence alors à 0 €).

Par ailleurs, le BDE peut supprimer la demande d'inscription sans problème via un bouton dédié. Cette opération
n'est pas réversible.

L'utilisateur a enfin accès a sa note et peut faire des bêtises :)

L'inscription au BDE et à la Kfet est indépendante de l'inscription au WEI. Voir `WEI <wei>`_ pour l'inscription WEI.
