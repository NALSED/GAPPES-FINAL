Les trois états d'une source ou d'un outil, avec le même vocabulaire pour les deux.

**La pastille ne porte jamais l'information seule.** Elle est toujours suivie du mot, parce qu'une couleur
seule n'est pas lisible par tout le monde — c'est le critère WCAG 1.4.1, et c'était déjà la règle du
pilote. Un rond vert sans le mot « opérationnelle » est une erreur.

Les trois mots sont fermés : **opérationnelle**, **à vérifier**, **éteinte**. Au féminin pour une source,
au masculin pour un outil. Jamais « actif », « OK », « en ligne ».

La pastille fait 10 px, `rayon-rond`, et prend `etat-ok`, `etat-attention` ou `etat-eteint`. Les trois
tiennent au moins 3:1 sur les trois fonds.

En étiquette dans un panneau, le fond est `etat-…-fond` et le texte `etat-ok-encre`, `etat-attention` ou
`encre-douce`, en `rayon-pilule`.

**Une nouvelle source ou un nouvel outil démarre à « à vérifier »** jusqu'à son premier test réussi. Ce
n'est pas une erreur, c'est l'état normal de ce qui n'a pas encore servi.

Le consommateur fournit l'état et le type d'objet ; le composant ne décide de rien.