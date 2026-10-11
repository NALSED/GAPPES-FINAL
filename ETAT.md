# ETAT — grappes

Dernière mise à jour : 2026-10-11 (cycle réel après Q24 : Admiralty, registres, Tranco). Référence unique : `FINAL.md` (les fichiers de `docs/archive/` sont obsolètes).

## En attente de Sednal

* Sujet(s) : fourni (`config/sujets.yaml`).
* Clés des fournisseurs : fournie (Tavily, `config/secrets.env`).
* Limites : fournies (`config/autonomie.yaml`).
* Activation de `autonome` : **activé** (`true`).

## Où on en est

* **Fait, selon `FINAL.md` § 14** : corrections du § 3 et nettoyage des fichiers obsolètes ; corpus synthétique à 3 grappes (~540 observations, formats réels) ; parcours complet jusqu'à `resultat.csv` (`tests/test_bout_en_bout.py`) ; robustesse et charge (lecture en flux, 500 000 enregistrements en 9,5 s) ; multiprise (YAML `http`, client MCP, plugins Python) ; amorçage depuis une phrase ; récupérateur de pages publiques ; ingestion automatique ; boucle `grappes cycle` avec apprentissage borné, recalibrage, instantanés, retour en arrière et rapport ; sortie finale `resultat.csv` (une colonne `NOM`) ; D25 (table d'équivalence Telegram) ; bilan des jetons.
* **Collectes réelles lancées** (`autonome: true`, Tavily, Wikipédia, RSS) : voir les sections ci-dessous et `rapports/`.
* v1 conservée : `ingest → run → export`, `explain`, `purge`, serveur MCP en lecture seule (8 outils), lecteurs de fichiers X, Telegram, Instagram et web (plus le chemin principal).
* Documents : `docs/conception/cycle.md` (boucle), `docs/conception/phase8.md` (multiprise), `docs/conception/formats_json.md`, `docs/conception/charge.md`, `docs/utilisateur.md` ; correctifs proposés pour `MISSION.md` : `docs/conception/corrections_mission.md`.
* Journal du compte gratuit : `donnees/.journal_ccr.log` (tâches mécaniques uniquement). Aucune interruption « session limit » constatée ; une coupure du serveur tmux le 2026-10-11 (`RELANCE.md`), reprise sans perte.

## Cycle réel avec le nouveau sujet (2026-10-11) — décisions Q22 et Q23 appliquées

Sujet : « Les acteurs des blocages et mobilisations étudiantes en France en ce moment ». Fournisseurs : Tavily (web), Wikipédia (écosystème `wikipedia`), flux RSS de L'Étudiant et de Libération (écosystème `rss`). Rapport du cycle propre : `rapports/cycle_2026-10-11_6.md` (c'est le cycle n° 9 du journal ; les cycles 5 et 6, qui avaient ingéré du bruit, ont été annulés par `grappes rollback`, voir D48 et D49).

* **Résultat** : 10 sources ingérées, 7 **probables**, **0 confirmée**. `sorties/resultat.csv` : L'Étudiant, Le Bonbon, Mouvement contre le contrat première embauche de 2006, Mouvement lycéen et étudiant de 2026 en France, Mouvements étudiants en France, Mouvements lycéens, Union nationale des étudiants de France. Pertinent pour les articles Wikipédia et L'Étudiant ; Le Bonbon (magazine culturel parisien) est du bruit.
* **Q22 appliquée** (D46) : écosystèmes `rss` et `wikipedia`, distincts de `web`. Wikipédia : 10 articles par requête, avec leurs liens externes ; les articles de personnes physiques sont écartés (7 par cycle). RSS : `robots.txt` consulté avant chaque flux. Wikidata n'est pas branché (explication dans D46). Google Actualités est écarté : son flux interdit expressément tout usage automatique.
* **Q23 appliquée** (D47) : nouveau sujet ; `seuil_ingestion` auto-ajustable dans [5 ; 40], départ 20. Il s'est ajusté seul au cycle 6 (20 → 25, « 3 sources sur 10 rangées : trop de bruit »), tracé dans le rapport ; cet ajustement a été annulé avec le cycle. Dans le cycle propre : inchangé (7 sources sur 10 rangées).
* **Règles tenues** : `robots.txt` respecté (flux et pages), 1 s entre deux requêtes d'un domaine, arrêt sur 403, aucun réseau social visité, journal complet (`donnees/journal_recherche.log` : 25 requêtes Tavily, 36 Wikipédia/RSS, 195 pages sur l'ensemble des cycles de la journée, annulés compris).
* **Défauts de mon code corrigés en route** : D48 (les 8 premiers articles Wikipédia prenaient tous les emplacements de « nouvelles sources » : plafond désormais partagé entre écosystèmes) et D49 (requêtes avec des variantes du même mot ; un mot répété suffisait à faire ingérer un article : deux radicaux distincts exigés).

## Q24 : pondération Admiralty, registres, Tranco appliqués (D50 à D53)

* **Fait** : fiabilité A à F par type de fournisseur (poids par centroïde de rang, aucun barème inventé), crédibilité 1 à 6, colonne `admiralty` dans `entites.csv` ; registres officiels (ESR par domaine : 241 domaines en cache ; SIRENE/RNA par nom exact, actif, unique) ; Tranco (liste 8PXYV du 2026-10-10, téléchargée une fois, cache 30 jours). 515 tests verts.
* **Cycle réel après les trois points** (`rapports/cycle_2026-10-11_7.md`) : 4 nouvelles sources, sources par lettre B : 2, C : 11, D : 1, **aucune en A** (le seul nom web interrogé, « Le Bonbon », n'a pas de correspondance exacte), **0 entité confirmée**, 7 rangées « probable ». Rien n'a changé de grappe ; l'ajustement automatique du seuil d'ingestion (20 → 25) a été proposé par le cycle.
* **Lecture honnête** : la pondération rend la confirmation *plus rapide* quand deux écosystèmes citent la même cible (tests), mais elle ne crée pas de recoupement : tant que les citants d'une cible sont tous de l'écosystème `wikipedia`, la règle des deux écosystèmes bloque, comme voulu (D50, D51). Ce n'est pas un bug ; le résultat reste « probable » pour ce sujet. Les voies restantes de Q24 (extraction d'entités dans le texte RSS, plus de pages web) changent la règle ou le volume : non traitées sans décision de Sednal.

## Q24 suite : citations par mention textuelle (D54)

* **Fait** : le texte libre des éléments RSS et des pages web peut citer une entité déjà connue (nom exact ou domaine, jamais de création d'entité, jamais d'approximation, jamais le propre site de l'éditeur). Marquage `via="texte"`, fiabilité Admiralty une lettre en dessous de celle du citant. 522 tests verts.
* **Cycle réel** (`rapports/cycle_2026-10-11_8.md`) : 345 citations dont **7 par texte** (pages `lebonbon.fr` et `valeursactuelles.com` mentionnant « Union étudiante », « Cocarde étudiante », « Mouvement des gilets jaunes »), **toutes vers des articles Wikipédia** (donc cibles d'écosystème `wikipedia`, citantes `web`). Résultat : toujours **0 confirmée**, 8 probables. Aucun flux RSS ne mentionne par son nom une entité connue ce cycle.
* **Lecture honnête** : la mention textuelle apporte bien une seconde voix d'un autre écosystème, mais il faut encore trois citants membres et une somme de poids ≥ 3. Avec des sources D (mention = E, poids 0,59), il en faudrait beaucoup ; seules des mentions par des médias établis (B → C) y arrivent vite. Le plafond n'est donc plus la règle des deux écosystèmes mais le volume de sources citant les mêmes cibles. Je n'ai rien relâché (non négociable) et n'ai pas augmenté les pages lues (écarté).

* **Flux franceinfo ajouté (D55)** puis cycle réel (`rapports/cycle_2026-10-11_9.md`) : 1 seule observation du flux assez proche du sujet (95 résultats refusés pour proximité), 347 citations dont 9 par texte, toujours **0 confirmée**, 8 probables. Le Monde écarté (flux « usage strictement personnel », robots.txt restrictif).
* **Constat** : le sujet du jour ne produit presque aucun élément de flux proche ; ajouter des flux ne suffit pas. Je m'arrête là sur Q24 : la suite (autres médias, sujets plus couverts par la presse) demande un choix de Sednal. Rien n'est relâché.

## Limites connues

* Q16 à Q19 (formats Telegram, X, Instagram, web) restent ouvertes : elles se trancheront sur les premières vraies données collectées.
* L'identité d'un canal Telegram absent de `config/telegram.yaml` est une hypothèse (D33) : ses citations sont conservées mais ne valident jamais un recoupement.

## Économies de jetons

`ECONOMIES.md` (régénérable : `.venv/bin/python outils/bilan_jetons.py`) : appels routés vers le compte gratuit et gain RTK, présenté comme une estimation. Voir `docs/utilisateur.md`.

## Rapports de cycle

`rapports/cycle_<date>.md` (créés par `grappes cycle`, lisibles par un non-informaticien) ; dernier : `rapports/dernier_cycle.md`.
