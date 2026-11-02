# 08 — Plan de travail (Recherche avancée)

## Ce qu'on implémente

Un **canevas libre**, dans l'esprit de n8n : on pose des tuiles où on veut, on les déplace à la souris,
puis **on tire les liens soi-même**. C'est la pièce la plus lourde du pilote.

## Le modèle de données

Deux listes, et rien d'autre.

````
nodes : [ { id, nom, role, x, y, removable, opts, cat? } ]
edges : [ { id, from, to } ]
````

Les coordonnées `x` et `y` sont **portées par la tuile**, pas calculées par une mise en page automatique.
Une version antérieure plaçait les tuiles par colonnes selon leur rôle : **c'est abandonné**, ça
empêchait de poser une brique où on voulait.

## La règle que Sednal a corrigée en cours de route

**On pose les tuiles d'abord, on fait les liens après.** Poser une brique ne la relie à rien,
automatiquement, jamais. Une première version reliait la nouvelle tuile à la précédente : c'est faux, ce
n'est pas le fonctionnement de n8n, et ça enlève à l'utilisateur la maîtrise de son plan.

Une tuile fraîchement posée est **isolée**. C'est normal, et la fenêtre d'Aide le signalera si elle le
reste.

## Les gestes

| Geste | Effet |
| :-- | :-- |
| Clic sur une brique de la palette | Pose la tuile à un emplacement libre, **sans lien** |
| Appuyer-glisser sur une tuile | Déplace la tuile |
| Appuyer sur le **port de sortie**, puis cliquer une autre tuile | Crée le lien |
| Clic sur un lien | Le sélectionne, un bouton de retrait apparaît |
| Clic sur le fond | Désélectionne tout, annule un lien en cours |
| Clic sur une tuile | Ouvre **la fenêtre de la tuile** |
| Bouton **Ranger** | Range les tuiles en colonnes, sans toucher aux liens |

Pendant qu'un lien se tire, affiche un **trait pointillé** entre le port de départ et le pointeur. Sans
ce retour visuel, l'utilisateur ne sait pas qu'il est en train de relier.

Distingue bien un **clic** d'un **glisser** : un déplacement ouvre la fenêtre de tuile au relâchement si
la souris n'a pas bougé. Garde un drapeau « a bougé » pendant le glissement.

## La tuile

Carré de **64 px**, `rayon-tuile` (14 px), `ombre-posee`, pictogramme du rôle à **28 px** au centre, nom
dessous. Un **port de sortie** à droite, un **port d'entrée** à gauche, ronds (`rayon-rond`), bordés en
`trait-fort`.

Tuile sélectionnée : anneau en `accent`. Un `×` à 12 px dans le coin pour la retirer — *retirer*, pas
*supprimer* : la tuile sort du plan, rien n'est effacé.

Deux tuiles particulières : **Ta saisie** (le départ) et **Grappes** (l'arrivée). Elles ne se retirent
pas. *Ta saisie* n'a pas de rôle, donc pas de couleur de rôle : elle prend `encre-douce`.

## Les liens

Des **courbes de Bézier**, pas des traits droits, en `trait-fort`. Ajoute un tracé transparent et épais
par-dessus chaque lien pour en faire une cible cliquable : un trait de 1,6 px est impossible à attraper.

Un lien sélectionné passe en `accent` et fait apparaître un bouton de retrait à son milieu.

## La fenêtre d'une tuile

Clic sur une tuile → une fenêtre centrée de **1040 px**, en **trois colonnes** :

| Colonne | Contenu |
| :-- | :-- |
| **ENTRÉE** | Ce que la tuile reçoit, et la liste des tuiles qui la nourrissent. Depuis là on relie ou on retire un lien entrant. |
| **LA TUILE** | Le nom, le rôle, les options de la brique, son effet dans le Tableau de bord |
| **SORTIE** | Ce que la tuile renvoie, et la liste des tuiles qu'elle nourrit. Même chose en sortie. |

Les textes d'entrée et de sortie viennent des champs *Ce qu'il reçoit* et *Ce qu'il renvoie* de la fiche
outil (`06`). Les options sont celles de la fiche, reprises telles quelles.

Une tuile sans lien entrant affiche explicitement qu'elle n'en a pas, avec la liste de celles qu'on peut
y relier. C'est là que l'utilisateur répare son plan.

Pied de fenêtre : *Fermer* — on ne faisait que lire — et *Retirer la tuile* à droite, séparé.

## La palette

Colonne de gauche, repliable par groupe : **Outils** d'abord, puis les catégories de sources. Chaque
entrée porte son nom et une marque à droite :

- `+` en `accent` — posable
- *posée* en `encre-pale` — déjà sur le plan, clic sans effet
- *éteinte* en `encre-pale` — éteinte dans Réglages, clic sans effet

## Ranger

Le bouton *Ranger* replace les tuiles en colonnes par profondeur : une tuile est d'autant plus à droite
qu'elle a d'étapes avant elle. **Il ne touche à aucun lien.** C'est un confort de lecture, pas une
correction de plan.

## Où regarder

- `charte/composants/Tuile/` — anatomie exacte, ports, liens, états
- `maquettes/Recherche.dc.html` — tout le comportement, dans `renderVals()`
