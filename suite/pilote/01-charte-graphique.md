# 01 — Charte graphique : les jetons

## Ce qu'on implémente

Un fichier de style global qui déclare tous les jetons, et **plus aucune valeur de style écrite ailleurs
dans le code**. C'est la toute première étape : chaque écran qui suit s'en sert.

## La règle

Aucune couleur, taille de texte, graisse, espacement, rayon ni ombre ne s'écrit en dur. Jamais un
`#2563A8`, jamais un `13px`, jamais un `border-radius: 10px` dans un composant. Toujours
`var(--accent)`, `var(--rayon-carte)`.

Si une valeur te manque, **elle n'existe pas** : ne l'invente pas dans ton coin, demande qu'on l'ajoute
à la charte. C'est exactement comme ça que le pilote s'est retrouvé avec 39 couleurs et 11 tailles de
texte avant qu'on reprenne tout.

## Comment faire

Inclure `charte/jetons.css` tel quel, au niveau le plus haut. Il déclare tout sur `:root`.

````css
/* bon */
.carte { background: var(--surface); border: 1px solid var(--trait); border-radius: var(--rayon-carte); }

/* interdit */
.carte { background: #fff; border: 1px solid #E3E5E8; border-radius: 10px; }
````

## Ce qu'il y a dedans

**32 couleurs**, en quatre familles. Les surfaces (`surface`, `surface-page`, `surface-creuse`), les
traits (`trait` décoratif, `trait-fort` porteur d'information), les encres (`encre`, `encre-douce`,
`encre-pale`), l'accent, les états, et six paires de rôles.

**10 styles de texte** : `etiquette`, `legende`, `corps`, `corps-fort`, `controle`, `titre-s`, `titre-m`,
`titre-l`, `chiffre`, `code`. Rien entre les deux. Police **IBM Plex Sans**, et **IBM Plex Mono** pour le
seul style `code`.

**Espacements** : base de 4 px, de `espace-1` (4 px) à `espace-8` (32 px). Rien entre deux pas.

**Rayons** : `rayon-controle` 6 px (ce qu'on manipule), `rayon-carte` 10 px (ce qui contient),
`rayon-tuile` 14 px (les tuiles du plan de travail et elles seules), `rayon-pilule` (étiquettes),
`rayon-rond` 50 % (pastilles, ports). **Le rayon dit ce qu'est l'objet** — ne les mélange pas.

**Ombres** : `ombre-posee`, `ombre-carte`, `ombre-panneau`, `ombre-fenetre`. L'ombre dit la hauteur, donc
l'urgence. Une seule ombre franche dans grappes : `ombre-fenetre`, pour ce qui bloque la page.

## Les contrastes sont calculés, pas choisis

Chaque valeur de `tokens.json` porte un champ `usage` qui donne son rapport de contraste mesuré. Ils
respectent le WCAG 2.2 : **4,5:1** pour le texte courant (critère 1.4.3), **3:1** pour les bords et
pictogrammes porteurs d'information (critère 1.4.11).

Plusieurs couleurs du pilote d'origine échouaient et ont été corrigées — le gris pâle du texte, l'orange
d'avertissement, le gris des bords et des liens. **Ne reviens pas aux anciennes valeurs** même si elles
te paraissent plus jolies : elles ne passaient pas.

Et le critère 1.4.1 : **jamais la couleur seule**. Une pastille d'état est toujours accompagnée de son
mot. Une étiquette de rôle porte toujours son texte.

## Un seul thème

La charte est en clair uniquement, parce que le pilote est en clair. Pas de thème sombre pour l'instant
— mais comme tout passe par des jetons, en ajouter un plus tard ne touchera aucun composant.

## Où regarder

- `charte/jetons.css` — à inclure
- `charte/tokens.json` — les mêmes valeurs, avec la justification de chacune
- `charte/README.md` — le livret complet et les références externes
