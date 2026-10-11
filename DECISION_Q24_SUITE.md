# Suite de Q24 : extraction de citations dans le texte (apres Admiralty/Tranco/registres)

D50 a D53 sont bons et restent en place. Ils n'ont pas resolu Q24 : c'est attendu, le poids
accelere une confirmation existante, il ne cree pas une deuxieme voix independante.

## Decision
Ajoute l'extraction de citations dans le TEXTE LIBRE des elements RSS et des pages web
(en plus des liens explicites deja geres). Contrainte stricte, non negociable :
- Reconnait UNIQUEMENT des noms d'entites DEJA CONNUES (deja en base, via un lien explicite
  ou un cycle precedent). JAMAIS de creation d'entite nouvelle a partir du seul texte.
- Correspondance par nom exact ou variante deja enregistree. Pas d'approximation floue,
  pas de reconnaissance de nom libre non deja catalogue.
- Marque ce type de citation differemment d'une citation par lien (ex. via="texte"), avec
  sa propre fiabilite Admiralty (une mention textuelle pese probablement moins qu'un lien
  explicite : a toi de juger et documenter dans DECISIONS.md).
- Garde "probable" par defaut la ou aucun recoupement, textuel ou par lien, n'est trouve.
- Options "beaucoup plus de pages" et "citer son propre flux" restent ecartees (deja tranche).

Tests : une citation textuelle vers une entite connue valide un recoupement si elle vient
d'un ecosysteme different ; vers un nom inconnu, aucune entite n'est creee ; un nom
partiellement ressemblant n'est pas confondu avec l'entite connue.

Applique, documente (DECISIONS.md, statut "proposee"), puis relance un cycle reel.
