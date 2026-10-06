# Guide utilisateur

## Flux

1. `grappes ingest <dossier> --ecosystem x|telegram|web` : lit les `.json` / `.jsonl`, normalise, stocke (idempotent sur `obs_id`). Affiche nouvelles observations, doublons, rejets.
2. `grappes run` : scoring sémantique, citations, recoupement itératif borné, affectation. Le `run_id` dépend des observations et de la configuration : rejouer donne le même résultat.
3. `grappes export --out ./sorties` : `entites.csv` (une ligne par entité) et `appartenances.csv` (format long).
4. `grappes explain <entity_id> [--grappe G]` : preuves (termes trouvés, citants, validation par recoupement).
5. `grappes purge --older-than 180` : supprime les observations plus anciennes que N jours.
6. `grappes mcp` : serveur MCP lecture seule (voir `README.md`).

## Configuration (`config/`)

* `grappes/*.yaml` : une grappe par fichier (`id`, `label`, `scale`, `lexicon.terms`, `lexicon.negative`, `anchors`, `oppositions`). Les lexiques réels sont à fournir ; ceux du dépôt sont des démonstrations neutres.
* `sources.yaml` : poids par écosystème et surcharges par source.
* `scoring.yaml` : seuils (`seuil_min`, `marge_ambiguite`, niveaux), poids de la confiance, `crossref` (`min_citers`, `min_ecosystems`, `min_weight_sum`, `min_citer_confidence`, `window_days`), `crossref_floor`, `max_iter`, format CSV.
* `config_hash` (empreinte des fichiers) est enregistré avec chaque run.

## Lire le CSV

* `cluster_id` : grappe principale ; vide si `non_classé` (confiance < `seuil_min`).
* `confidence_level` : `confirmé` ≥ 70, `probable` ≥ 40, `faible` sinon.
* `status` : `classé`, `ambigu` (grappe proche ou opposée), `non_classé`.
* `validated_via_crossref` : `oui` si l appartenance principale vient du recoupement.
* Confiance = S + (100 − S)·(0,6·E + 0,4·A) / 100 (S sémantique, E recoupement, A ancrage, tous sur 0 à 100). Sans citations, confiance = S. Valeurs initiales, configurables (`poids_complementaire`, voir `DECISIONS.md` D15). L'ancienne formule 0,5·S + 0,3·E + 0,2·A reste disponible avec `formule_confiance: ponderee` (poids dans `poids_confiance`).
* Proximité sémantique : 100 × (1 − exp(−brut / scale)), `scale = 3` par défaut (par grappe). Un terme de poids 1 donne ≈ 28, trois termes ≈ 63 (D7).

## Limites connues

* Formats JSON d entrée proposés, non réels (Q2) : `docs/conception/formats_json.md`.
* Les liens `t.me` créent une entité `web:t.me`.

## Corpus synthétique

````bash
.venv/bin/python outils/corpus_synthetique.py /tmp/corpus   # x/, telegram/, web/, attendu.json
.venv/bin/grappes --db /tmp/corpus/c.db ingest /tmp/corpus/x --ecosystem x
````

Thèmes neutres inventés, graine fixe : mêmes fichiers à chaque génération. `attendu.json` donne le statut attendu des cibles de recoupement (validé, refusé, ambigu).

