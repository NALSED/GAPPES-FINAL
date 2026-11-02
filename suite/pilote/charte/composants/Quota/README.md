Ce qu'il reste d'appels autorisés sur une source, pour la période en cours.

La jauge fait 6 px de haut, `rayon-pilule`, sur un fond `etat-eteint-fond`. Elle est en `accent` jusqu'à
79 %, et passe en `etat-attention` **à partir de 80 %**. Ce seuil est le même partout dans grappes.

**Le pourcentage est écrit à côté de la jauge**, et il passe à la même couleur. Une barre qui change de
couleur sans chiffre lisible retombe dans le défaut que la charte interdit : la couleur seule.

Les chiffres prennent `font-variant-numeric: tabular-nums`, pour que les colonnes s'alignent d'une ligne
à l'autre.

Le libellé dit la source, le consommé, le plafond et la période : « OpenSanctions · 4 120 / 5 000 ce
mois ». Une source sans quota affiche un tiret, pas une jauge vide.

Le consommateur fournit le consommé, le plafond et la période ; le composant calcule le reste.