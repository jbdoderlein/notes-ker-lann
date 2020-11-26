Transferts
==========

Affichage
---------

L'interface de la page de transferts est semblable à celles des consommations, et l'auto-complétion de note est géré de
la même manière. La page se trouve à l'adresse ``/note/transfer/``. La liste des 20 transactions les plus récentes que
l'utilisateur a le droit de voir est également présente.

Des boutons ``Don``, ``Transfert``, ``Crédit``, ``Retrait`` sont présents, représentant les différents modes de
transfert. Pour chaque transfert, un montant et une description sont attendus.

Onglet transferts
-----------------

Cet onglet est visible par tout le monde. Il permet d'effectuer un transfert depuis plusieurs notes vers d'autres notes,
à l'image des consommations doubles. Si une erreur survient (permission insuffisante), un message d'erreur apparaîtra.

Onglets Crédit et retrait
-------------------------

Ces onglets ne sont visibles que par ceux qui ont le droit de voir les ``SpecialNote``.

Une boîte supplémentaire apparaît, demandant en plus de la note, du montant et de la raison le nom, le prénom et
la banque de la personne à recharger/retirer. Lorsqu'une note est sélectionnée, les champs "nom" et "prénom" sont
remplis automatiquement. Par ailleurs, seule une note peut être choisie.

Transfert
---------

Les transferts se font à nouveau via l'API, avec le même schéma que précédemment, en remplaçant
``RecurrentTransaction`` par ``Transaction`` simplement pour don/transfert, et ``SpecialTransaction`` pour
crédit/retrait, en adaptant le champ ``polymorphic_ctype``.
