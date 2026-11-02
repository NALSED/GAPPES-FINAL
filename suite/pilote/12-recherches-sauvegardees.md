# 12 — Recherches sauvegardées

## Ce qu'on implémente

Une liste des recherches enregistrées, qu'on peut relancer telles quelles.

## Ce qu'une entrée porte

| Champ | Exemple |
| :-- | :-- |
| Titre | `Associations sportives Isère` |
| Mode | `Simple` ou `Avancée` |
| Catégories | `assos`, `lieux` |
| Détail | `Associations : club de judo · Lieux : Isère` |
| Date | `22/10 · 18:30` |
| Résultat | `27 grappes` |

## Les deux actions

**Réutiliser** — recharge la recherche dans l'écran dont elle vient : la Recherche simple si elle y a été
faite, le plan de travail si elle vient de là. Pictogramme `reutiliser`.

**Supprimer** — c'est le **seul objet de grappes qui se supprime**. Définitif, donc **fenêtre
d'avertissement obligatoire** avant (voir `charte/composants/Avertissement/`). Pictogramme `supprimer`,
bouton en `danger`.

Ne confonds pas avec *Retirer*, qui n'existe pas ici : il n'y a rien à sortir d'une liste sans effacer.

## Une recherche avancée garde son plan

Réutiliser une recherche avancée doit restituer **les tuiles à leurs coordonnées et tous les liens**, pas
seulement la liste des sources. Enregistre `nodes` et `edges` tels quels (voir `08`).

## Où regarder

- `charte/composants/Avertissement/`
- `maquettes/Recherche.dc.html`, carte « Recherches sauvegardées »
