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
* **Phase 7** : plan écrit (`docs/conception/phase7.md`, D17, proposée), non exécuté ; attend de vrais exports (Q2, Q16 à Q19) ; Q7 levée (D21). Aucune donnée réelle ingérée.
* **Réponses n°2 appliquées** : D19 (Q15 : E = 0 tant que le recoupement n'est pas validé, `recoupement_partiel` et `e_potentiel` dans `explain`), D20 (Q7 : pas de `retention_days`, pas de `redact_persons`). Q7 et Q7b levées ensuite (D21).
* **Revue de configuration** (D22) : `ConfigError` lisibles partout, NaN/infini refusés, ancres canonicalisées et validées, `purge` négatif refusé ; `tests/test_config_robustesse.py`.
* **CLI** (D23) : `ingest` échoue explicitement si tout est rejeté ; paquet installé dans `.venv` (commande `grappes` disponible) ; ingestion incrémentale testée sur le corpus.
* **Échantillons de formats** (`REPONSES_SEDNAL_3.md`, D24 à D26) : comparaison documentée dans `docs/conception/formats_json.md` ; fetchers X, Telegram, web adaptés, `InstagramFetcher` créé, liens révisés (D14 -> D24) ; `tests/test_echantillons.py` (échantillons dans `tests/fixtures/echantillons/`). Points à confirmer sur de vrais exports : Q16 à Q19. Aucune donnée réelle ingérée, aucune ré-identification.
* Tests : 177 verts, `ruff` propre.
* Interruptions « session limit » : aucune constatée depuis les réponses de Sednal (à noter ici à chaque occurrence, Q13).

## Ce qui marche

* Pipeline complet `ingest → run → export`, `explain`, `purge`, serveur MCP (voir phases 1 à 6).

## Constats d'environnement

* `gh` n'est pas installé : impossible de commenter l'issue `NALSED/agent-momo`. Les questions sont dans `QUESTIONS.md` et le pilotage se fait par tmux (§0).
* Hook `Stop` et hook rtk (`PreToolUse`) actifs. `python` et `ruff` ne sont pas dans le PATH : utiliser `.venv/bin/`.
* Interruption : `/opt/grappes` était en `root:root` 755 au début de la session ; corrigé par Sednal.

## Limites connues

* Les invitations Telegram, publications Instagram et raccourcis `t.co` ne citent rien (D24) ; l'identité des canaux Telegram repose sur le nom affiché (D25, Q16).

## Reste à faire

* Vrais exports (Sednal) pour lever Q16 à Q19 ; phase 7 (`docs/conception/phase7.md`) ensuite.
* Réponses de Sednal encore ouvertes : Q3 (langues), Q10 (clients MCP), Q11 (embeddings).
* Pas de watchdog « session limit » (Q13) ; noter chaque interruption ici.
