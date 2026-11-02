# 16 — Onglet Tri

## Ce qu'on implémente

L'écran de validation humaine des rapprochements proposés par le rôle RAPPROCHER (aujourd'hui, la source
« Fusion/doublons »). C'est la réponse à la question ouverte n° 10 de `14-questions-ouvertes.md`, tranchée
le 26/10/2026.

**Lis d'abord ceci** : aucun moteur de rapprochement sérieux ne fusionne deux fiches sans qu'une personne
confirme. C'est vrai pour Aleph (étape *xref*, voir `source.md` §2.5) comme pour Splink (voir
`15-mecanismes-et-references.md` §1). Grappes ne fait pas exception — c'est même la pièce qui manquait le
plus, parce que sans elle, RAPPROCHER fusionnerait des fiches sur la seule confiance d'un score.

## Pourquoi l'onglet s'appelle Tri

Ce n'est pas un hasard de vocabulaire : l'onglet existait déjà, vide, sous ce nom. *Trier* un rapprochement
— décider s'il tient ou non — est exactement le sens du mot. Rien à renommer.

## La file

Une liste de **rapprochements** (voir `charte/nommage.md`, section « Les objets ») : des paires de fiches
que RAPPROCHER soupçonne de parler de la même entité, pas encore tranchées. **Triée du moins certain au
plus certain** — c'est le travail le plus incertain qui mérite l'attention en premier, et un rapprochement
évident ne doit pas faire attendre un rapprochement douteux derrière lui.

Une ligne d'en-tête donne le compte : « n rapprochements à examiner, du plus incertain au plus certain. »

## La carte d'un rapprochement

Une carte par rapprochement, dans cet ordre :

1. **En-tête** : pictogramme `rapprocher`, un titre court, et la **confiance** à droite — une barre et un
   pourcentage. La confiance est **calculée, jamais saisie** : c'est le score que rend le moteur de
   rapprochement (Splink, voir `15-mecanismes-et-references.md` §1), pas une appréciation de l'utilisateur.
2. **Les fiches, côte à côte**, une colonne par fiche, deux aujourd'hui (un rapprochement à trois fiches ou
   plus reste possible plus tard, même disposition). Chaque colonne porte :
   - la **source** d'origine et sa **fiabilité** (lettre A–F, voir `05-reglages-sources.md`) ;
   - les propriétés comparables, **une ligne par propriété**, dans le même ordre des deux côtés pour que
     l'œil compare sans chercher.
3. **Le dire visuel de la comparaison**, calculé champ par champ, jamais écrit en dur :
   - les deux valeurs **identiques** (une fois normalisées — casse, espaces) → fond `etat-ok-fond`, texte
     `etat-ok-encre` ;
   - les deux valeurs **présentes mais différentes** → fond `etat-attention-fond`, texte `etat-attention` ;
   - une valeur **absente d'un côté** → texte `encre-pale` en italique, jamais traité comme une différence
     puisqu'il n'y a rien à comparer.
4. **Le pied** : *Confirmer* en bouton principal, *Séparer* en secondaire. Aucun des deux n'est un bouton
   danger — ni l'un ni l'autre n'efface quoi que ce soit (voir plus bas).

## Confirmer / Séparer : deux nouveaux verbes, ajoutés le 26/10/2026

Aucun verbe existant ne disait ce geste. Ajoutés à la liste close de `charte/nommage.md` :

- **Confirmer** : le rapprochement est accepté, les fiches fusionnent dans la grappe.
- **Séparer** : le rapprochement est refusé, les fiches restent distinctes. Pas « Rejeter » — le mot est
  plus dur que ce que fait réellement l'action, qui ne supprime ni ne pénalise aucune fiche.

Ni l'un ni l'autre n'est *Retirer* ni *Supprimer* : aucun fichier, aucune fiche, aucune source n'est
touché. Les deux gestes ne décident que du lien entre deux fiches, et les deux se refont — c'est à ça que
sert la section suivante.

## Déjà tranchés

Une carte repliable, fermée par défaut, sous la file. Chaque rapprochement tranché y migre avec une
étiquette *Confirmé* ou *Séparé* et son moment. **Rien ne disparaît en silence** : la règle n° 1 de
`00-MAIN.md` (on garde toujours l'original) vaut aussi pour une décision de tri — elle doit rester lisible,
pas seulement appliquée.

## État vide

Quand la file est vide : « Aucun rapprochement à examiner. Fusion/doublons n'a rien trouvé de nouveau
depuis la dernière recherche. » Pas d'icône de célébration, pas de ton badin — une file vide est un état
normal, pas un succès à souligner.

## Ce qui n'est pas encore construit

- **La crédibilité de l'information (1–6, code Admiralty)** : elle s'appliquera à chaque propriété d'une
  fiche de résultat, qui n'est pas encore maquettée. Elle n'intervient pas dans cet écran aujourd'hui — la
  confiance affichée ici est celle du rapprochement, pas celle d'une valeur isolée. Les deux se recoupent
  mais ne sont pas la même chose : voir `15-mecanismes-et-references.md` §2.
- **Un rapprochement à trois fiches ou plus** : la maquette n'illustre que des paires. La disposition en
  colonnes s'étend sans changement de principe.
- **Le lien avec RAPPROCHER sur le plan de travail** : comment une tuile RAPPROCHER alimente concrètement
  cette file (push direct, file d'attente partagée) reste à l'implémentation ; ce document fixe l'écran,
  pas le tuyau qui l'alimente.

## Où regarder

- `maquettes/Tri.dc.html` — la maquette interactive, avec trois exemples (34 %, 68 %, 95 %) illustrant un
  nom proche sans identifiant, un nom identique sans identifiant, et un identifiant SIREN identique.
- `charte/nommage.md` — section « Les verbes d'action » (Confirmer, Séparer) et « Les objets » (fiche,
  rapprochement).
- `15-mecanismes-et-references.md` §1 — Splink, le moteur qui calcule la confiance.
- `source.md` §2.5 — la même idée chez Aleph (xref, deux étages, décision humaine), pour comparer.
