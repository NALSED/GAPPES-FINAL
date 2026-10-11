# ETAT — grappes

Dernière mise à jour : 2026-10-11. Référence unique : `FINAL.md` (les fichiers de `docs/archive/` sont obsolètes).

## En attente de Sednal

* Sujet(s) : fourni (`config/sujets.yaml`).
* Clés des fournisseurs : fournie (Tavily, `config/secrets.env`).
* Limites : fournies (`config/autonomie.yaml`).
* Activation de `autonome` : **activé** (`true`).

## Où on en est

* **Fait, selon `FINAL.md` § 14** : corrections du § 3 et nettoyage des fichiers obsolètes ; corpus synthétique à 3 grappes (~540 observations, formats réels) ; parcours complet jusqu'à `resultat.csv` (`tests/test_bout_en_bout.py`) ; robustesse et charge (lecture en flux, 500 000 enregistrements en 9,5 s) ; multiprise (YAML `http`, client MCP, plugins Python) ; amorçage depuis une phrase ; récupérateur de pages publiques ; ingestion automatique ; boucle `grappes cycle` avec apprentissage borné, recalibrage, instantanés, retour en arrière et rapport ; sortie finale `resultat.csv` (une colonne `NOM`) ; D25 (table d'équivalence Telegram) ; bilan des jetons.
* **Aucune collecte réelle n'a été lancée** : `autonome` est faux, aucun fournisseur n'est branché, tous les tests utilisent de faux serveurs locaux.
* v1 conservée : `ingest → run → export`, `explain`, `purge`, serveur MCP en lecture seule (8 outils), lecteurs de fichiers X, Telegram, Instagram et web (plus le chemin principal).
* Documents : `docs/conception/cycle.md` (boucle), `docs/conception/phase8.md` (multiprise), `docs/conception/formats_json.md`, `docs/conception/charge.md`, `docs/utilisateur.md` ; correctifs proposés pour `MISSION.md` : `docs/conception/corrections_mission.md`.
* Journal du compte gratuit : `donnees/.journal_ccr.log` (tâches mécaniques uniquement). Aucune interruption « session limit » constatée ; une coupure du serveur tmux le 2026-10-11 (`RELANCE.md`), reprise sans perte.

## Premier cycle réel (2026-10-11)

Sujet : « Les acteurs de l'actualité française en ce moment ». Fournisseur : Tavily (14 requêtes en tout, dont 1 de vérification et 6 d'un cycle annulé). Rapport le plus récent : `rapports/dernier_cycle.md` (cycle 4) ; historique : `rapports/cycle_2026-10-11*.md`.

* **Résultat** : 5 sources **probables**, **0 confirmée**. `sorties/resultat.csv` : Made in Marseille, OpenAI, Parlons Politique, Serieously. L'ensemble est modeste et de pertinence inégale (la phrase du sujet est large : « acteurs » ramène aussi des sites de cinéma ou d'IA).
* **Règles tenues** : `robots.txt` lu pour chaque hôte (13 à 16 pages refusées par `robots.txt` à chaque cycle) ; 1 s au moins entre deux requêtes d'un même domaine ; arrêt sur 403 (`themeforest.net`, `openai.com` selon le cycle) ; aucun réseau social ni domaine interdit visité ; chaque appel est dans `donnees/journal_recherche.log` ; la clé n'apparaît ni dans le dépôt, ni dans les journaux, ni dans les rapports.
* **Retour en arrière** : aucun déclenchement automatique (aucun indicateur dépassé). Un retour manuel (`grappes rollback`) a servi à annuler le premier cycle après correction de défauts de mon code (D44).
* **Pourquoi aucune confirmée, et pourquoi la boucle d'apprentissage n'a encore rien appris** : « confirmée » exige un recoupement sur au moins 2 écosystèmes. Avec Tavily seul, toutes les sources lues sont du web : un seul écosystème. Tant qu'aucun adaptateur officiel (Telegram, X, Instagram...) n'est branché comme fournisseur, aucune entité ne peut être confirmée, donc ni apprentissage de mots, ni recalibrage (voir Q22).
* **Formats (Q16 à Q19)** : Q19 (web) **confirmée en partie** — de vraies pages donnent bien titre, texte, `site_name` (4 sources sur 5 ont un nom lisible), langue, liens avec ancre ; la date de publication d'une page n'est pas extraite (on garde la date de récupération). **Q16, Q17, Q18 non testables** : les réseaux ne sont pas lus, donc aucun export Telegram, aucun JSON X ni Instagram n'a été vu. Seuls leurs **liens** ont été observés sur de vraies pages : `x.com/<compte>` cite bien `x:<compte>` ; une publication Instagram (`/p/...`) ne cite rien, comme prévu (D24). Réponse de Tavily conforme à la documentation (`title`, `url`, `content`, `score`, `published_date` pour 4 résultats sur 8, `raw_content`, `id`).
* **Défauts de mon code trouvés et corrigés grâce à ces données** : D44, D45. Un incident de test (appels réels possibles depuis la suite de tests avec la vraie clé) est aussi corrigé, D43.

## Limites connues

* Q16 à Q19 (formats Telegram, X, Instagram, web) restent ouvertes : elles se trancheront sur les premières vraies données collectées.
* L'identité d'un canal Telegram absent de `config/telegram.yaml` est une hypothèse (D33) : ses citations sont conservées mais ne valident jamais un recoupement.

## Économies de jetons

`ECONOMIES.md` (régénérable : `.venv/bin/python outils/bilan_jetons.py`) : appels routés vers le compte gratuit et gain RTK, présenté comme une estimation. Voir `docs/utilisateur.md`.

## Rapports de cycle

`rapports/cycle_<date>.md` (créés par `grappes cycle`, lisibles par un non-informaticien) ; dernier : `rapports/dernier_cycle.md`.
