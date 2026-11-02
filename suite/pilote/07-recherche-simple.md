# 07 — Recherche simple

## Ce qu'on implémente

Le chemin court : on choisit un préréglage, on tape ce qu'on cherche, on lance. **Il doit marcher seul**,
sans jamais obliger l'utilisateur à ouvrir le plan de travail.

## Un préréglage

Un ensemble de sources d'une catégorie, prêt à l'emploi. Les préréglages reprennent les catégories de
Réglages : Entreprises, Associations, Presse, Lieux…

On en choisit un par **puce** (`Puce`), une seule à la fois.

## Le détail des sources : cases, pas puces

Une fois le préréglage choisi, la liste de ses sources apparaît avec une **case à cocher** par source.
Toutes cochées par défaut ; l'utilisateur en décoche.

**La distinction compte.** Une *puce* sert à choisir parmi quelques possibilités visibles d'un coup —
c'est le préréglage. Une *case* sert à activer ou désactiver indépendamment dans une longue liste — ce
sont les sources. Ne les intervertis pas, même si ça se ressemble à l'écran. Voir
`charte/composants/Puce/README.md`.

Une source **éteinte** dans Réglages apparaît décochée et non cochable, avec son état visible.

## Remettre par défaut

Dès que l'utilisateur décoche quelque chose, un bouton **Remettre par défaut** apparaît et recoche tout
le préréglage. Verbe pris dans la liste close, pas « Réinitialiser ».

## La saisie et le lancement

Un champ de saisie, puis **Lancer la recherche** en bouton principal avec le pictogramme `lancer`.
**Un seul bouton principal** sur l'écran.

## Le pays

Un sélecteur de pays séparé, qui filtre les sources concernées. `Tous` par défaut.

## Ce qui doit rester vrai

L'utilisateur qui ne touche jamais à la Recherche avancée doit pouvoir travailler **complètement** avec
cet écran. La recherche simple n'est pas une démo : c'est le mode normal. Le plan de travail est pour
ceux qui veulent sortir des préréglages.

## Où regarder

- `charte/composants/Puce/` — la distinction puce / case, avec les deux rendus
- `charte/composants/Carte/`, `Bouton/`
- `maquettes/Recherche.dc.html`, carte « Recherche simple »
