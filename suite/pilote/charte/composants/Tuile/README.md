La tuile du plan de travail, dans la recherche avancée.

Un carré de 64 px en `rayon-tuile` — le seul endroit de grappes qui emploie ce rayon — avec le
pictogramme du rôle à **28 px** au centre, dans la couleur `role-…`. Sous la tuile, son nom en
`corps-fort` et son rôle en `legende` et `encre-pale`.

**Les ports.** Un rond de 14 px à gauche pour l'entrée, un à droite pour la sortie, en `trait-fort` qui
tient le 3:1. « Ta saisie » n'a pas d'entrée, « Grappes » n'a pas de sortie, et c'est ce qui dit le sens
du parcours. Le port de sortie est un vrai `<button>` avec son `aria-label`, parce qu'on tire le lien
depuis lui.

**Les liens** sont des courbes de Bézier en `trait-fort`, 1,6 px, de la sortie d'une tuile vers l'entrée
d'une autre. Un lien choisi passe en `accent` et épaissit à 2,4 px.

**Sélectionnée**, la tuile prend un contour `accent`, un halo de 3 px, et son `×` de retrait apparaît en
haut à droite. Le halo ne remplace pas le contour : les deux sont là.

La tuile « Ta saisie » prend `encre-douce` : elle n'a pas de rôle, c'est le point de départ.

La tuile de résultat « Grappes » est la seule à fond `accent-fond` : elle n'est pas une brique qu'on pose,
c'est l'arrivée.

Le fond du plan de travail est `surface-creuse` avec une trame de points de 18 px. On pose d'abord les
tuiles, puis on tire les liens, comme dans n8n.

Le consommateur fournit les tuiles avec leur position, et la liste des liens.