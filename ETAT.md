# ETAT — grappes

Dernière mise à jour : 2026-10-06 — Phase 0 (préparation, aucun code applicatif).

## Où on en est

* `MISSION.md` lu en entier (fichier tronqué à la Q5 du §17, voir `QUESTIONS.md`).
* Fichiers de suivi créés : `ETAT.md`, `DECISIONS.md`, `QUESTIONS.md`, `docs/conception/`.
* `MISSION.md` mis à jour par Sednal : plage 9 h à 17 h supprimée (développement continu).
* Migration §4.2 : étapes 1 à 4 faites (dépôt git dédié `/opt/grappes`, `CLAUDE.md`, `outils/continuer.sh`, `outils/appeler_gratuit.sh` testé : 1 ligne dans `donnees/.journal_ccr.log`).
* Étape 5 (`~/.claude/settings.json`, hook `Stop`) : **bloquée**, l'édition a été refusée par le classifieur de permissions. À faire par Sednal ou à autoriser explicitement. Sauvegarde non faite.
* Étapes 6 (nouvelle session tmux) et 7 (checklist §4.7) en attente.

## Ce qui marche

* Rien d'applicatif (phase 0).

## Constats d'environnement

* `gh` n'est pas installé : impossible de commenter l'issue `NALSED/agent-momo`. Les questions sont dans `QUESTIONS.md` et le pilotage se fait par tmux (§0).
* `~/.claude/settings.json` référence toujours `/opt/mapping/outils/continuer.sh` (hook `Stop`). Non modifié (interdit avant accord de Sednal).
* Interruption : `/opt/grappes` était en `root:root` 755 au début de la session ; corrigé par Sednal.

## Reste à faire

* Réponses de Sednal aux questions de `QUESTIONS.md`.
* Validation puis exécution des étapes 1 à 7 du §4.2.
* Phase 1 après validation de la phase 0.
