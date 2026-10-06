# ETAT — grappes

Dernière mise à jour : 2026-10-06 — v1 terminée (phases 0 à 6) ; réponses de Sednal appliquées (`REPONSES_SEDNAL.md`).

## Où on en est

* Phase 0 terminée (suivi, `CLAUDE.md`, outils, dépôt git dédié). Pleine autonomie : plus de STOP de fin de phase (D6).
* Phase 1 terminée : squelette, `models.py`, `canon.py`, `BaseFetcher` + registre, fetchers X/Telegram/web, fixtures synthétiques, `docs/conception/formats_json.md`.
* Phase 2 terminée : `semantic/scoring.py` + tests §9.1 (voir D7 sur l'écart de la valeur « ≈ 86 »).
* Phase 3 terminée : SQLite (`storage/db.py`), config YAML + `config_hash`, affectation sémantique seule (confiance = S), `entites.csv` / `appartenances.csv` rejouables à l'identique, CLI `ingest`/`run`/`export`.
* Phase 4 terminée : poids des sources, citations, recoupement itératif borné (`ecosystem/crossref.py`), ancres et oppositions (`semantic/relations.py`), confiance complète (`clustering/assign.py`), table `validations`. Cas testés : validé, refusé (écosystèmes, citants, poids, non-membres), ambigu, circularité bornée.
* Phase 5 terminée : serveur MCP (`mcp/queries.py`, `mcp/server.py`), 8 outils, SDK `mcp` 2.3.0 épinglé (D13), README de connexion ; test de bout en bout via un client MCP stdio.
* Phase 6 terminée : CLI complète (`ingest`, `run`, `export`, `explain`, `purge`, `mcp`), erreurs d'entrée lisibles, `docs/utilisateur.md`, test de charge 100 000 observations : 5,0 s, ~200 Mo (`docs/conception/charge.md`).
* **v1 fonctionnelle** : `ingest → run → export` sur fixtures, `explain`, MCP. Reste hors code : voir « Reste à faire ».
* Tests : 83 verts (`.venv/bin/pytest`), `ruff` propre.
* Journal gratuit : 8 lignes dans `donnees/.journal_ccr.log` (N à fixer, Q14).
* Étape 5 de §4.2 faite : le hook `Stop` de `~/.claude/settings.json` pointe vers `/opt/grappes/outils/continuer.sh`, plus aucune référence à `/opt/mapping`, sauvegarde `settings.json.bak` (QB réglée).

* **Réponses de Sednal appliquées** : D7 confirmé (`scale = 3`, un terme ≈ 28, trois ≈ 63) ; D15 formule de confiance `S + (100 − S)·(0,6·E + 0,4·A)/100` (ancienne formule en option `formule_confiance: ponderee`) ; D13 import `mcp.server.mcpserver.MCPServer` confirmé ; Q1, Q4, Q5, Q9, Q12, Q13, Q14, QA, QC réglées ou provisoires.
* **Revue de robustesse** (D16) : BOM UTF-8 accepté, fichier JSON illisible compté comme rejet, injection de formule CSV neutralisée ; 31 tests (`tests/test_robustesse.py`).
* **Corpus synthétique** (D18) : `outils/corpus_synthetique.py` (~2 300 enregistrements), `tests/test_corpus.py` ; requête MCP « 10 sources les plus influentes de la Grappe A » vérifiée (API et client stdio).
* **Phase 7** : plan écrit (`docs/conception/phase7.md`, D17, proposée), non exécuté ; bloquée par Q2 et Q7. Aucune donnée réelle ingérée.
* **Réponses n°2 appliquées** : D19 (Q15 : E = 0 tant que le recoupement n'est pas validé, `recoupement_partiel` et `e_potentiel` dans `explain`), D20 (Q7 : pas de `retention_days`, pas de `redact_persons`). Base légale non précisée (Q7b).
* Tests : 137 verts, `ruff` propre.
* Interruptions « session limit » : aucune constatée depuis les réponses de Sednal (à noter ici à chaque occurrence, Q13).

## Ce qui marche

* Pipeline complet `ingest → run → export`, `explain`, `purge`, serveur MCP (voir phases 1 à 6).

## Constats d'environnement

* `gh` n'est pas installé : impossible de commenter l'issue `NALSED/agent-momo`. Les questions sont dans `QUESTIONS.md` et le pilotage se fait par tmux (§0).
* Hook `Stop` et hook rtk (`PreToolUse`) actifs. `python` et `ruff` ne sont pas dans le PATH : utiliser `.venv/bin/`.
* Interruption : `/opt/grappes` était en `root:root` 755 au début de la session ; corrigé par Sednal.

## Limites connues

* Les liens d'invitation Telegram (`t.me/+...`, `joinchat`) restent des entités `web:t.me` : pas de canal public identifiable (D14, Q2).

## Reste à faire

* Réponses de Sednal : Q2 (JSON anonymisés), Q7b (base légale), Q3, Q10, Q11.
* Phase 7 (données réelles) : dès que Q2 et Q7b sont répondues, suivre `docs/conception/phase7.md`.
* Pas de watchdog « session limit » (Q13) ; noter chaque interruption ici.
