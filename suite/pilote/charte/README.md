Cette charte couvre tout le pilote de grappes : les onglets Tableau de bord, Recherche, Réglages et Tri,
et chaque panneau, fenêtre et tuile qu'ils contiennent. Elle fixe l'apparence et les mots, jamais les
fonctionnalités. Une page qui respecte ces règles est cohérente avec les autres sans qu'on ait à comparer.

Trois références la fondent, et aucune règle ici n'est inventée pour l'occasion : le **système de design
Carbon d'IBM** pour les pictogrammes et la famille IBM Plex, déjà en place dans le pilote ; le **GOV.UK
Design System** pour la rédaction des boutons et des libellés d'une interface d'administration ; et
**WCAG 2.2** pour les contrastes, critères 1.4.3, 1.4.11 et 1.4.1.

## Les mots d'abord

Un mot par action, le même partout dans grappes. Les trois quarts de la confusion viennent de là, pas des
couleurs. La section « Les mots de grappes » donne la liste complète ; voici la règle.

Écris les boutons en minuscules, avec le verbe qui nomme exactement ce qui va se passer. Un seul bouton
principal par écran. Tutoie la personne, comme le pilote le fait déjà : « Choisis un modèle »,
« Ce que tu cherches ». Ne nomme jamais la même action de deux façons : une source se **retire**, une
recherche sauvegardée se **supprime**, et ces deux verbes ne sont pas interchangeables — retirer est
réversible et ne touche à aucun fichier, supprimer est définitif.

Les capitales servent à une seule chose : les en-têtes de colonne et les sur-titres, dans le style
`etiquette`. Un bouton, un onglet ou un titre en capitales est une erreur.

## Les couleurs

Trente-neuf couleurs circulaient dans le pilote avant cette charte. Il y en a trente-deux ici, toutes
nommées, chacune avec son emploi — et plus aucune valeur posée à la main.

Le fond de la page est `surface-page`, les blocs posés dessus sont en `surface`, et ce qui est en retrait
— en-tête de tableau, en-tête de carte repliable, fond du plan de travail — est en `surface-creuse`.
C'est le fond qui détache un bloc, pas son contour : `trait` est décoratif et ne doit jamais être le seul
signe qu'un élément existe. `trait-fort` est l'inverse : le contour d'un champ, d'une tuile, d'un port ou
d'un lien porte une information, donc il tient le 3:1 exigé.

Le texte prend `encre`, `encre-douce` pour le second rang, `encre-pale` pour le troisième. Ne descends pas
plus clair : `encre-pale` est déjà le gris le plus clair qui reste lisible sur les trois fonds.

`accent` est réservé à l'action principale et à la sélection : fond du bouton principal, onglet actif,
anneau de focus, ligne choisie. Il ne sert jamais de décoration. Un écran avec deux accents n'a plus
d'action principale.

Les six rôles ont chacun leur paire `role-…` et `role-…-fond`, et ces couleurs ne servent qu'aux rôles.
Les trois états ont leur paire `etat-…`. `danger` ne paraît que sur retirer et supprimer.

## Les états

Trois états, jamais plus : **opérationnelle**, **à vérifier**, **éteinte**. Ils valent pour les sources
comme pour les outils, avec le même vocabulaire et la même pastille. Une nouvelle source ou un nouvel
outil démarre « à vérifier » jusqu'à son premier test réussi.

La pastille ne porte jamais l'information seule : elle est toujours suivie du mot. C'est la règle du
pilote depuis le départ, et c'est aussi le critère WCAG 1.4.1. Même chose pour un quota : la jauge passe
en `etat-attention` à partir de 80 %, et le pourcentage est écrit à côté.

## La typographie

IBM Plex Sans pour tout, IBM Plex Mono pour un script collé ou un point de terminaison. Neuf styles de
texte, pas un de plus : onze tailles différentes circulaient avant, dont une à 12,5 px.

`corps` est le texte courant et doit rester le plus fréquent. `controle` habille les boutons, les champs
et les onglets. Les trois titres vont du plus petit au plus grand : `titre-s` pour une carte, `titre-m`
pour un panneau ou une fenêtre, `titre-l` pour la page — et un seul `titre-l` par écran.

## Les espaces et les rayons

Tout vient d'une base de 4 px, de `espace-1` à `espace-8`, et rien ne se glisse entre deux pas. Compose
les écarts avec `gap` sur un conteneur en flex ou en grille, pas avec des marges élément par élément.

Le rayon dit la nature de l'objet, et c'est la règle la plus simple à vérifier d'un coup d'œil :
`rayon-controle` pour ce qu'on manipule, `rayon-carte` pour ce qui contient, `rayon-tuile` pour les tuiles
du plan de travail et elles seules, `rayon-pilule` pour les étiquettes et les puces, `rayon-rond` pour les
pastilles et les ports. Neuf rayons traînaient dans le pilote, dont un à 7 px.

## Les pictogrammes

Un seul jeu, décrit par le composant Pictogrammes : vingt-huit dessins sur une grille de 24, trait de
1,6 px, extrémités arrondies, aucun remplissage. Deux tailles seulement : **20 px** dans les lignes, les
boutons et les panneaux, **28 px** sur les tuiles du plan de travail. Ne change jamais le rapport entre un
pictogramme et le texte à côté.

Un pictogramme prend la couleur du texte qu'il accompagne, selon la règle de Carbon — donc `encre-douce`
dans une ligne, `role-…` sur une étiquette de rôle, blanc dans un bouton principal. Il est centré sur le
texte, pas aligné sur sa ligne de base.

Un dessin ne veut dire qu'une chose dans tout grappes, et une chose n'a qu'un dessin. C'est pour cela que
l'engrenage est l'onglet Réglages et que les curseurs sont le rôle OUTIL : le pilote employait les
curseurs pour les deux.

Un pictogramme seul, sans libellé, ne s'emploie que dans les trois cas du composant Pictogrammes, et il
porte alors un `aria-label`. Partout ailleurs il accompagne un mot.

## Ce que cette charte attend d'une page

Avant de poser une page nouvelle dans grappes, vérifie ces sept points.

1. Chaque couleur vient d'un nom de cette charte, aucune valeur écrite à la main.
2. Un seul bouton principal, et son verbe figure dans « Les mots de grappes ».
3. Chaque état est une pastille **et** un mot.
4. Les en-têtes de colonne sont le seul texte en capitales.
5. Les pictogrammes sont à 20 px, ou à 28 px sur une tuile, et prennent la couleur du texte voisin.
6. Le rayon de chaque bloc correspond à sa nature.
7. Le focus au clavier se voit : un anneau `accent` de 2 px, décollé de 2 px, sur tout élément qu'on peut
   atteindre au clavier. Ne le retire jamais.

## Ce que la charte ne couvre pas encore

Un seul thème, clair, parce que le pilote n'en a qu'un. Un thème sombre s'ajouterait ici, pas dans les
pages. Les écrans du Tableau de bord et de l'onglet Tri ne sont pas encore dessinés : quand ils le seront,
ils prendront ces mêmes jetons sans en ajouter.
