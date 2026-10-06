# ETAT — grappes

Dernière mise à jour : 2026-10-06 — Phase 0 (préparation, aucun code applicatif).

## Où on en est

* Phase 0 terminée (suivi, `CLAUDE.md`, outils, dépôt git dédié). Pleine autonomie : plus de STOP de fin de phase (D6).
* Phase 1 terminée : squelette, `models.py`, `canon.py`, `BaseFetcher` + registre, fetchers X/Telegram/web, fixtures synthétiques, `docs/conception/formats_json.md`.
* Phase 2 terminée : `semantic/scoring.py` + tests §9.1 (voir D7 sur l'écart de la valeur « ≈ 86 »).
* Phase 3 en cours : SQLite, config YAML, affectation sémantique seule, `entites.csv` v0.
* Tests : 34 verts (`.venv/bin/pytest`), `ruff` propre.
* Journal gratuit : lignes dans `donnees/.journal_ccr.log` (N à fixer, Q14).
* Étape 5 de §4.2 (hook `Stop` dans `~/.claude/settings.json`) toujours à faire par Sednal (QB).

## Ce qui marche

* Ingestion JSON brut -> Observations (3 écosystèmes), rapport de rejets, doublons.
* Scoring de proximité 0 à 100.

## Constats d'environnement

* `gh` n'est pas installé : impossible de commenter l'issue `NALSED/agent-momo`. Les questions sont dans `QUESTIONS.md` et le pilotage se fait par tmux (§0).
* `~/.claude/settings.json` référence toujours `/opt/mapping/outils/continuer.sh` (hook `Stop`). Non modifié (interdit avant accord de Sednal).
* Interruption : `/opt/grappes` était en `root:root` 755 au début de la session ; corrigé par Sednal.

## Reste à faire

* Réponses de Sednal aux questions de `QUESTIONS.md`.
* Validation puis exécution des étapes 1 à 7 du §4.2.
* Phase 1 après validation de la phase 0.
