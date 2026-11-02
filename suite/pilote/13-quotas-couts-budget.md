# 13 — Quotas, coûts, budget

## Ce qu'on implémente

Trois mécanismes liés : ce qu'il reste d'appels sur une source, ce que coûtent les sources payantes, et
l'arrêt avant dépassement.

## Le quota d'une source

Déclaré dans la fiche source : un nombre et une unité (`par jour`, `par mois`, `par semaine`). Vide =
**illimité**.

Affiché dans la colonne QUOTA de la liste : une **jauge** et les chiffres. Les chiffres en
`font-variant-numeric: tabular-nums`, sinon la colonne danse quand les valeurs changent.

### Le seuil de 80 %

À partir de **80 %**, la jauge et le chiffre passent en `etat-attention`. Ni avant, ni à 100 % — à 100 %
il est trop tard pour réagir.

Une source **éteinte** affiche *éteinte*, pas une jauge à zéro : ce n'est pas la même information.

## L'outil Attente (quota)

Fait patienter la recherche quand un quota est atteint, au lieu de la faire échouer. Options : ce qu'on
fait quand le quota tombe (*attendre*), et une attente maximale (`10 minutes` par défaut).

Éteint d'origine : à allumer par celui qui en a besoin.

## L'outil Compteur budget

Arrête la recherche avant de dépasser un budget. Options : budget maximum (`5 € par mois`), et un
avertissement à partir de **80 %** — le même seuil que les quotas, volontairement.

Effet dans le Tableau de bord : `alerte`.

Éteint d'origine.

## Ce que le contrôle de plan en fait

Le contrôle n° 5 de `verifier_plan()` (voir `11`) signale toute source posée dont le quota dépasse 80 %
ou est atteint, en niveau *remarque* : la recherche tournera, mais s'arrêtera en route.

## Le coût

Colonne COÛT dans la liste des sources : `gratuit`, ou le tarif. C'est une information déclarée dans la
fiche, pas calculée.

L'état des clés d'API et des quotas réels de chaque source est tenu dans
`../cles-api-26.10.2026.md`, à la racine du dépôt.

## Où regarder

- `charte/composants/Quota/` — la jauge, le seuil, les chiffres
- `maquettes/Main.dc.html` — `quotaView()`
