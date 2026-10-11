# ETAT — grappes

Dernière mise à jour : 2026-10-11. Référence unique : `FINAL.md` (les fichiers de `docs/archive/` sont obsolètes).

## En attente de Sednal

* Un ou plusieurs sujets, en une phrase chacun (`config/sujets.yaml`).
* Les clés des fournisseurs de recherche branchés (variables d'environnement).
* Les limites générales : quotas, profondeur d'exploration, liste d'interdits (`config/autonomie.yaml`).
* L'activation de `autonome` (`config/autonomie.yaml`, false par défaut) ; fichier d'arrêt immédiat `donnees/STOP`.

## Où on en est

* **Fait, selon `FINAL.md` § 14** : corrections du § 3 et nettoyage des fichiers obsolètes ; corpus synthétique à 3 grappes (~540 observations, formats réels) ; parcours complet jusqu'à `resultat.csv` (`tests/test_bout_en_bout.py`) ; robustesse et charge (lecture en flux, 500 000 enregistrements en 9,5 s) ; multiprise (YAML `http`, client MCP, plugins Python) ; amorçage depuis une phrase ; récupérateur de pages publiques ; ingestion automatique ; boucle `grappes cycle` avec apprentissage borné, recalibrage, instantanés, retour en arrière et rapport ; sortie finale `resultat.csv` (une colonne `NOM`) ; D25 (table d'équivalence Telegram) ; bilan des jetons.
* **Aucune collecte réelle n'a été lancée** : `autonome` est faux, aucun fournisseur n'est branché, tous les tests utilisent de faux serveurs locaux.
* v1 conservée : `ingest → run → export`, `explain`, `purge`, serveur MCP en lecture seule (8 outils), lecteurs de fichiers X, Telegram, Instagram et web (plus le chemin principal).
* Documents : `docs/conception/cycle.md` (boucle), `docs/conception/phase8.md` (multiprise), `docs/conception/formats_json.md`, `docs/conception/charge.md`, `docs/utilisateur.md` ; correctifs proposés pour `MISSION.md` : `docs/conception/corrections_mission.md`.
* Journal du compte gratuit : `donnees/.journal_ccr.log` (tâches mécaniques uniquement). Aucune interruption « session limit » constatée ; une coupure du serveur tmux le 2026-10-11 (`RELANCE.md`), reprise sans perte.

## Limites connues

* Q16 à Q19 (formats Telegram, X, Instagram, web) restent ouvertes : elles se trancheront sur les premières vraies données collectées.
* L'identité d'un canal Telegram absent de `config/telegram.yaml` est une hypothèse (D33) : ses citations sont conservées mais ne valident jamais un recoupement.

## Économies de jetons

`ECONOMIES.md` (régénérable : `.venv/bin/python outils/bilan_jetons.py`) : appels routés vers le compte gratuit et gain RTK, présenté comme une estimation. Voir `docs/utilisateur.md`.

## Rapports de cycle

`rapports/cycle_<date>.md` (créés par `grappes cycle`, lisibles par un non-informaticien) ; dernier : `rapports/dernier_cycle.md`.
