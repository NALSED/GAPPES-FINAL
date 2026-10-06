# ETAT — grappes

Dernière mise à jour : 2026-10-06 — v1 terminée (phases 0 à 6), consolidation.

## Où on en est

* Phase 0 terminée (suivi, `CLAUDE.md`, outils, dépôt git dédié). Pleine autonomie : plus de STOP de fin de phase (D6).
* Phase 1 terminée : squelette, `models.py`, `canon.py`, `BaseFetcher` + registre, fetchers X/Telegram/web, fixtures synthétiques, `docs/conception/formats_json.md`.
* Phase 2 terminée : `semantic/scoring.py` + tests §9.1 (voir D7 sur l'écart de la valeur « ≈ 86 »).
* Phase 3 terminée : SQLite (`storage/db.py`), config YAML + `config_hash`, affectation sémantique seule (confiance = S), `entites.csv` / `appartenances.csv` rejouables à l'identique, CLI `ingest`/`run`/`export`.
* Phase 4 terminée : poids des sources, citations, recoupement itératif borné (`ecosystem/crossref.py`), ancres et oppositions (`semantic/relations.py`), confiance complète (`clustering/assign.py`), table `validations`. Cas testés : validé, refusé (écosystèmes, citants, poids, non-membres), ambigu, circularité bornée.
* Phase 5 terminée : serveur MCP (`mcp/queries.py`, `mcp/server.py`), 8 outils, SDK `mcp` 2.3.0 épinglé (D13), README de connexion ; test de bout en bout via un client MCP stdio.
* Phase 6 terminée : CLI complète (`ingest`, `run`, `export`, `explain`, `purge`, `mcp`), erreurs d'entrée lisibles, `docs/utilisateur.md`, test de charge 100 000 observations : 5,0 s, ~200 Mo (`docs/conception/charge.md`).
* **v1 fonctionnelle** : `ingest → run → export` sur fixtures, `explain`, MCP. Reste hors code : les réponses de Sednal à Q1–Q7, Q9–Q14.
* Tests : 83 verts (`.venv/bin/pytest`), `ruff` propre.
* Journal gratuit : 8 lignes dans `donnees/.journal_ccr.log` (N à fixer, Q14).
* Étape 5 de §4.2 faite : le hook `Stop` de `~/.claude/settings.json` pointe vers `/opt/grappes/outils/continuer.sh`, plus aucune référence à `/opt/mapping`, sauvegarde `settings.json.bak` (QB réglée).

## Ce qui marche

* Pipeline complet `ingest → run → export`, `explain`, `purge`, serveur MCP (voir phases 1 à 6).

## Constats d'environnement

* `gh` n'est pas installé : impossible de commenter l'issue `NALSED/agent-momo`. Les questions sont dans `QUESTIONS.md` et le pilotage se fait par tmux (§0).
* Hook `Stop` et hook rtk (`PreToolUse`) actifs. `python` et `ruff` ne sont pas dans le PATH : utiliser `.venv/bin/`.
* Interruption : `/opt/grappes` était en `root:root` 755 au début de la session ; corrigé par Sednal.

## Limites connues

* Les liens vers `t.me` créent une entité `web:t.me` (site) au lieu d'une citation du canal Telegram : à traiter avec les vrais formats (Q2).

## Reste à faire

* Réponses de Sednal aux questions de `QUESTIONS.md` (Q1–Q7, Q9–Q14).
* `MISSION.md` ne définit pas de phase 7 : consolidation en attendant (revue de code, cas limites, lien `t.me`).
* Watchdog « session limit » : proposé (D4), non implémenté avant accord (Q13).
