# 03 — Vocabulaire

## Ce qu'on implémente

Une **liste close de mots**, centralisée dans le code comme les jetons de style. Chaque libellé affiché
vient de cette table. Pas de chaîne de caractères écrite directement dans un composant.

La liste complète est dans `charte/nommage.md`. Ce document-ci dit pourquoi ça compte et ce qui piège.

## Pourquoi c'est une étape à part

grappes est devenu complexe, au point que Sednal lui-même, qui l'a conçu, s'y perd. La cause n'est pas la
complexité du programme : c'est que la même chose porte trois noms selon l'écran. « Allumé », « actif »,
« opérationnelle » étaient tous les trois à l'écran en même temps.

Un mot par action, un mot par état, un mot par objet. **Si un écran a besoin d'un mot absent de la liste,
c'est la liste qu'on modifie d'abord**, pas l'écran.

## Le piège principal : retirer ≠ supprimer

C'est la distinction la plus importante, et la plus facile à casser en codant.

| Verbe | Ce qu'il fait | Réversible | Confirmation |
| :-- | :-- | :-- | :-- |
| **Retirer** | Sort de la liste ou du plan, ne touche à aucun fichier | oui | non |
| **Supprimer** | Efface pour de bon | **non** | **oui, une fenêtre** |

Dans le code, ce sont **deux opérations différentes**, pas un paramètre de la même. Ne les fusionne pas
sous prétexte qu'elles se ressemblent à l'écran.

Un seul objet se supprime aujourd'hui : la recherche sauvegardée. Partout ailleurs, c'est *retirer*.

## Les trois états, et l'accord

**opérationnelle**, **à vérifier**, **éteinte**.

Au féminin pour une **source**, au masculin pour un **outil** : « source opérationnelle », « outil
opérationnel ». Ça veut dire **deux tables de libellés**, pas une. Le pilote avait le bug : les tuiles
outils affichaient « opérationnelle ».

Jamais « actif », « inactif », « OK », « KO », « en ligne », « hors ligne ».

## Les six rôles

**CHERCHER**, **VÉRIFIER**, **ENRICHIR**, **CATALOGUE**, **OUTIL**, **RAPPROCHER**. En capitales, parce
que ce sont des étiquettes et pas des phrases — c'est la seule exception à la règle sur les capitales.

**RAPPROCHER remplace LIEN.** Depuis que le plan de travail relie des tuiles par des liens, « lien »
comme rôle était ambigu. Désormais un *lien* dans grappes est **toujours** la flèche entre deux tuiles.

## Les objets

source, outil, brique, tuile, lien, plan de travail, préréglage, grappe, quota. Définis dans
`charte/nommage.md`.

Dis « source », jamais « base », « connecteur » ou « fournisseur ». Dis « grappe », jamais « cluster »,
« groupe » ou « regroupement ».

## Le marquage IA

Un mot réservé : **IA**. Tout ce qu'un modèle écrit le porte, de sa production jusqu'à la grappe finale.
La marque ne se retire jamais en chemin. Voir `10-tuile-assistant-ia.md`.

## Deux objets à ne pas confondre

L'**Aide** est la fenêtre d'assistance en bas à droite. L'**Assistant IA** est un outil du plan de
travail. Deux objets, deux noms, deux endroits, deux documents. L'Aide ne s'appelle jamais « assistant ».

## Où regarder

- `charte/nommage.md` — la liste close complète
