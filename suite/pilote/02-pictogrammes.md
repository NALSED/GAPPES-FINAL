# 02 — Pictogrammes

## Ce qu'on implémente

Un jeu de **31 dessins SVG**, et aucun autre. Les tracés complets sont dans
`charte/composants/Pictogrammes/README.md`, sous forme de tableau : nom, emploi, attribut `d`.

Stocke-les dans **une seule table** du code, indexée par nom. Pas de SVG recopié à la main dans un
composant : c'est comme ça que le pilote s'est retrouvé avec deux chevrons différents et un trait à 1,7
au milieu de traits à 1,6.

## La forme, identique pour les 31

````html
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="…"/>
</svg>
````

Grille de 24, trait de **1,6**, bouts et angles arrondis, `fill="none"`. Aucun dessin n'est rempli.

## Deux tailles, et c'est tout

**20 px** dans les lignes, les boutons et les panneaux. **28 px** sur les tuiles du plan de travail.
Rien entre les deux.

Une seule exception, documentée : le `×` qui retire une tuile est à **12 px, trait de 2,4**, parce qu'il
tient dans un bouton de 20 px posé dans le coin de la tuile.

## La couleur vient du texte voisin

`stroke="currentColor"` et le pictogramme suit son contexte — c'est la règle d'IBM Carbon. Donc
`encre-douce` dans une ligne de tableau, la couleur du rôle sur une étiquette de rôle, `sur-accent` dans
un bouton principal.

Trois exceptions : `attention` est toujours en `etat-attention`, `aide` et `ia` sont en `accent` quand
ils annoncent la fenêtre d'aide ou un contenu produit par une IA.

## Un dessin, une seule chose

L'engrenage est **l'onglet Réglages**. Les curseurs sont **le rôle OUTIL**. Le pilote d'origine employait
les curseurs pour les deux — c'est corrigé, ne le refais pas.

La loupe sert à l'onglet Recherche **et** au rôle CHERCHER : ce n'est pas un doublon, c'est la même idée.

## Accessibilité

Un pictogramme **sans libellé** n'est permis que dans quatre cas : le `×` de fermeture, le chevron de
dépliage, les ports d'une tuile, le bouton d'envoi de l'Aide. Chacun porte alors un `aria-label`.
Partout ailleurs un pictogramme accompagne un mot, il ne le remplace pas.

Cible tactile d'au moins **44 px** : ajoute du remplissage autour du dessin, n'agrandis pas le dessin.

Un pictogramme est **centré** sur le texte voisin, jamais aligné sur sa ligne de base.

## Où regarder

- `charte/composants/Pictogrammes/README.md` — les 31 tracés et toutes les règles
- `charte/composants/Pictogrammes/preview.html` — les 31 dessins rendus, par groupe
