# ETAT — grappes

Dernière mise à jour : 2026-10-06. Référence unique : `FINAL.md` (les fichiers de `docs/archive/` sont obsolètes).

## En attente de Sednal

* Un ou plusieurs sujets, en une phrase chacun (`config/sujets.yaml`).
* Les clés des fournisseurs de recherche branchés (variables d'environnement).
* Les limites générales : quotas, profondeur d'exploration, liste d'interdits (`config/autonomie.yaml`).
* L'activation de `autonome` (`config/autonomie.yaml`, false par défaut) ; fichier d'arrêt immédiat `donnees/STOP`.

## Où on en est

* v1 terminée (phases 0 à 6) : `ingest → run → export`, `explain`, `purge`, serveur MCP en lecture seule, 8 outils. Lecteurs de fichiers X, Telegram, Instagram et web, conservés mais plus le chemin principal.
* Multiprise de recherche (`grappes search`, `src/grappes/search/`, D27, D28) : fournisseurs par fichier YAML (`http`, `mcp`) ou plugin Python ; dry-run tant que `autonome` est faux ; aucun appel réel lancé.
* Sortie finale `sorties/resultat.csv` (une colonne `NOM`), valeurs de cadre D30 (`retention_days` 90, `redact_persons` actif) : en cours d'application, voir `DECISIONS.md`.
* Reste à construire, dans l'ordre de `FINAL.md` § 14 : corpus synthétique à 3 grappes, test de bout en bout jusqu'à `resultat.csv`, robustesse et charge, amorçage, récupérateur de pages, ingestion automatique, boucle `grappes cycle`, rapport.
* Tests : voir la dernière exécution de `.venv/bin/pytest` ; `ruff` propre.
* Journal du compte gratuit : `donnees/.journal_ccr.log` (tâches mécaniques uniquement). Aucune interruption « session limit » constatée (à noter ici à chaque occurrence).

## Limites connues

* Q16 à Q19 (formats Telegram, X, Instagram, web) restent ouvertes : elles se trancheront sur les premières vraies données collectées.
* L'identité des canaux Telegram dérivée du nom affiché est une hypothèse (D25), à encadrer selon `FINAL.md` § 11.

## Rapports de cycle

`rapports/cycle_<date>.md` (créés par `grappes cycle`, lisibles par un non-informaticien) ; dernier : `rapports/dernier_cycle.md`.
