Deux façons de choisir, et elles ne se mélangent pas.

**La puce** sert à choisir parmi un petit nombre d'options visibles d'un coup : un pays, une catégorie, un
rôle. Elle fait 34 px de haut, `rayon-pilule`. Choisie : fond `accent-fond`, texte `accent-encre`, contour
`accent`, en gras. Non choisie : fond `surface`, contour `trait-fort`.

**La case** sert à allumer ou éteindre une source dans une liste longue, là où l'on balaie des dizaines de
lignes. Elle fait 18 px, coin de 4 px, et la coche est blanche sur `accent`. Une ligne décochée passe en
`encre-pale` : on voit d'un coup ce qui reste allumé.

Toutes deux sont de vrais `<button>` avec `aria-pressed`, jamais un `div` qui écoute le clic : sans quoi
on ne les atteint pas au clavier.

Le consommateur fournit le libellé, l'état et la fonction appelée au clic.