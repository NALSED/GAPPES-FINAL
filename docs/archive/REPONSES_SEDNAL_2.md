> **OBSOLÈTE** : remplacé par `FINAL.md` (référence unique, 2026-10-06). Conservé pour l'historique uniquement ; ne pas s'y référer.

# Réponses de Sednal n°2 — 06/10/2026

## Q15 : E et recoupement refusé

Décision : option (b), avec une partie de (c) pour l'observabilité.

* E vaut 0 tant que le recoupement n'est pas validé. Quand il est validé : E = 100 × min(1, Σ poids des citants / (2 × min_weight_sum)).
* Motif : un recoupement refusé (par exemple un seul écosystème) ne doit pas suffire à classer l'entité, sinon la règle de croisement d'écosystèmes est contournée.
* Le refus reste visible : `explain` affiche la ValidationRecord avec ses reasons (par exemple « écosystèmes 1 < 2 ») et un indicateur `recoupement_partiel` (E potentiel non retenu). Pas de nouvelle colonne dans entites.csv.
* `via` vaut `recoupement` seulement si le recoupement est validé ; sinon `semantique` ou `ancre` selon le cas.
* Tests : x:cible_mono_eco (5 membres de la grappe A, un seul écosystème) → refusé, E = 0, conf = S, non classé. Ajoute un second écosystème parmi les citants → validé, E > 0, classé via `recoupement`.
* Enregistre-le en D16 (proposée), mets à jour assign.py, la doc et les tests. Ne modifie pas MISSION.md.
