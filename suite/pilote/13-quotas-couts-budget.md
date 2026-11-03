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

## L'outil « Quand une source est à court » (ex-Attente)

« Attendre » a disparu (02/11/2026, retour de Sednal, document 3.8.07) : un quota qui se renouvelle vite
(par minute) est déjà réessayé automatiquement par le programme, et un quota qui se renouvelle lentement
(quotidien, mensuel) ne se rattraperait pas par une attente de quelques minutes. Un seul choix fermé reste :
sauter la source à court et continuer les autres (déjà le comportement par défaut), ou arrêter toute la
recherche — ce qui est déjà collecté est gardé, comme pour la limite d'appels.

Éteint d'origine : à allumer par celui qui en a besoin.

## L'outil Compteur budget

Arrête la recherche avant de dépasser un budget, en **crédits** — l'unité propre au programme (02/11/2026,
retour de Sednal, document 3.8.08 : le mot « dollar » disparaît partout où ce système l'employait, le
mécanisme ne change pas). « Budget maximum » est un montant fixe en crédits, ou un pourcentage du plafond
mensuel déjà réglé dans Réglages. Le seuil d'alerte (80 % par défaut) est réglable, avec une action fermée :
prévenir, ou ne rien faire.

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
