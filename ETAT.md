# ETAT — grappes

Phase en cours : revue totale du code (demande de Sednal du 09/11/2026 : revue, corrections, poussée sur main) — lot 909 (D112) et `pilote/src/pilote` (D113) revus et corrigés ; et `pilote/static` (D114) revus et corrigés ; reste le moteur `src/grappes` et les points non corrigés listés dans D113 et D114.

909 (« Vérifier et enrichir ») clos pour tout ce qui est câblable sans Sednal ni infra manquante : §1.1 fait
(D104), §2.1 complet (a/b/c, D104+D105), 1.2 (a/b/c/d) faits (D106/D92/D108/D107), 1.2 (e/f) déclinés avec
raisons vérifiées et tracées (D109, détail dans `pilote/QUESTIONS.md`), §3 (Requête avancée, 11e outil) fait
(D110), 1.3.d fait (D111). Confirmé par la spec elle-même (`fae02c6`, lu le 09/11) : sections 1/2/3 marquées
« prêtes pour momo », volet 2 (comparaison systématique ancienne UI/`/suite`) et §4 encore « pas actionnables ».
Reste dans 909 : 1.3 (a/b/c, process — revue OSINT Framework, filet honnête, agent `.60`, pas du code pilote),
le volet comparaison (second volet, plus large, pas détaillé point par point par la spec). §4 mis en attente
par la spec elle-même.

Prochain point « prêt pour momo » de `000-INDEX.md` : 903 pièce 2/2 (Cible de recherche) — mais touche le
moteur (`src/grappes/decouverte/verification_type.py`, `config/ner/*.yaml`), pas `pilote/`, et son
type-vérificateur est mesuré par la mission autocalibration/certification (critères gelés, jamais à modifier
sans décision explicite). Pas commencé sans instruction explicite — seul « commence 909 » avait été demandé.
(Ligne lue par le hook d'arrêt `outils/continuer.sh` : écrire « Phase en cours : <nom> » au début d'une phase, « aucune » à la fin.)

Dernière mise à jour : 2026-11-09 (D111 : §1.3.d — bug pré-existant découvert et corrigé, `ckan.yaml` déclarait
verifier/enrichir depuis l'import initial sans jamais poser `verifie_sur` (jamais réellement appelée comme
vérificatrice) ; même correctif + rôle verifier ajouté à `hdx.yaml`/`un-civil-society.yaml` (907). Nouveau
dossier `config/sources_candidates/` avec les trois candidats nommés par la spec (ICIJ Offshore Leaks,
entreprises exclues par les bailleurs, Open Ownership Register), tous `a_evaluer`, prêts pour la revue de
Sednal. Test ciblé vert ; suite complète hors réseau : 639 passés, 1 échec pré-existant.

D104 (précédent) : Sednal a demandé explicitement de commencer 909 malgré son état « en cours de rédaction »
— instruction directe qui prévaut sur la règle d'attente de validation écrite de `POUR_MOMO.md`. §1.1 fait :
bug critique corrigé (`allumer()` perdait « verifier » sur une source chercher+verifier rallumée), enrichir
devient un rôle indépendant (case par rôle, réglage global « Vérification active » exposé dans /suite).

D103 (précédent) : lu sur `NALSED/GRAPPES` (commit `da89dd0`) que Sednal a revu le calendrier — la
suppression de l'ancienne UI n'a plus lieu qu'à la toute fin du projet entier, et Tri attend la fin de toute
la tuyauterie outils/sources (909 et ce qui en découlera). 908 confirmée complète pour tout ce qui était à
ma main.

En attente de Sednal (plus tard dans la journée) : 905 §2 (vérification `.60`), 903 pièce 2/2 (décision Q27).

D102 (précédent) : 908 étape 6, point 1 — profondeur, limites de temps/d'appels et pause/reprise d'une
recherche en cours, portés dans `/suite` (pur portage, le moteur avait déjà tout). Suite relancée hors
réseau (624 passés, 1 échec pré-existant) ; navigateur (18 passés).

D101 (précédent) : 908 étape 5, point 13 — le curseur à quatre niveaux de l'Assistant IA ; seul le niveau 1 a
un mécanisme réel, les niveaux 2 à 4 sont refusés par le moteur avec une raison claire.

D100 (précédent) : 908 étape 5, point 14.1/14.2 — l'Aide parle au même agent que l'Assistant IA (suite_ia),
plus au serveur Ollama « pas tranché » ; même liste close de six fonctions sûres. Le volet « agir » documenté
dans QUESTIONS.md, pas construit dans la même passe.

D99 (précédent) : 908 étape 5, point 14.3/14.4 — l'inventaire du programme (`pilote.inventaire`) : sources,
outils, formats, opérations IA, vocabulaires fermés, actions, tous DÉCOUVERTS depuis le programme réel ; test
de complétude.

D95 (précédent) : 908 étape 4, point 9 — libellé « remplace » et aperçu de la Boucle sans rien lancer
(9.2/9.3) ; 9.1 (brancher les origines manquantes) NON fait : le code montre qu'aucune des trois origines ne
relance la recherche, contrairement à ce que décrivait le retour.

D94 (précédent) : 908 étape 4, point 2.3 — l'effet « alerte » du Compteur budget (seuil, action « Prévenir »)
rejoint enfin la section Alertes du Tableau de bord, évalué à la fin de chaque recherche.

D93 (précédent) : 908 étape 4, point 6.3 — destination des fichiers de sortie exposée dans la fiche Format
de sortie de `/suite`, vérifiée avant l'enregistrement.

D92 (précédent) : 908 étape 4, point 3.3 — le test réel d'une source (prix avant le clic, plafond mensuel)
exposé depuis `/suite` ; pur portage des routes de l'ancienne page.

D91 (précédent) : 908 étape 3 (6.1) — un vrai test pour « si »/Filtre/Format de sortie (exécution réelle,
même moteur que la tuile) ; les six genres non exécutables hors ligne (fusion, boucle, ia, rsshub, attente,
budget) ne peuvent plus afficher « opérationnel » sans preuve ; Traduction perd son bloc de test générique,
doublon de son test réel (7.2).

D90 (précédent) : 908 étape 2 — règle 3.10 appliquée : conditions « si »/Filtre en déroulants une par ligne,
différences Filtre/« si » visibles, Format de sortie en blocs repliables, langues de Traduction multiples.

D89 (précédent) : 908 étape 1 — fusion/rsshub en pastilles, Modèle masqué en modification d'un outil, textes
entiers, « illimité » corrigé pour une source payante, catégories de l'Assistant IA branchées, chemin en dur
et erreur Python brute corrigés côté Traduction.

D88 (précédent) : 905 §2 — MCP/fichier/base/base extérieure/programme local ajoutables depuis `/suite` ; 906 —
Scrapling branché (nouvel adaptateur générique, dépendance optionnelle) ; 907 — HDX et UN Civil Society
Database ajoutées en réel (`config/sources/hdx.yaml`, `un-civil-society.yaml`), testées de bout en bout sur le
vrai service.

903, pièce 1/2 faite (NER élargi à PER/LOC, commit `92c890e`) — prépare le filtre « Ce que je recherche » sans
encore le consommer. Pièce 2/2 (`TypeDemande` multi-natures, champ UI, export par cible) **en attente d'une
décision de Sednal** : le volet association/entreprise suppose le rattachement NAF de Q27 déjà fait, ce qui
n'est pas le cas (D82 : coûte des crédits réels, décidé pour une session dédiée) — je ne peux ni l'inventer ni
lancer la dépense seul. Q36 ouverte : 4 tests de `test_cycle.py` rouges, indépendants de ce travail (dérive
d'environnement, pas une régression de commit — détail dans QUESTIONS.md). Référence unique : `FINAL.md` (les
fichiers de `docs/archive/` sont obsolètes).

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

## Q24 : close (acceptée, D56)

Décision de Sednal : « probable » est le niveau maximal accepté pour le sujet actuel (trop pointu pour se recouper naturellement). D50 à D55 (Admiralty, registres, Tranco, mentions textuelles, flux franceinfo) restent en place pour d'autres sujets ; pas de nouveau flux, pas de changement de sujet, règle des deux écosystèmes inchangée. Dernier état : 8 probables, 0 confirmée (`rapports/cycle_2026-10-11_9.md`). Plus aucun point bloquant ouvert : les cycles reprennent selon le planning normal : timer systemd **quotidien à 04:00** installé (D57, service utilisateur), premier passage prévu le 2026-10-12 ; cycle de vérification du 2026-10-11 sans alerte (`rapports/cycle_2026-10-11_10.md`). D50 à D57 actées.

## Fiabilité des sorties (D58)

* **Une voix par éditeur** dans le recoupement : `agency.x.fr`, `x.fr` et le flux `rss:x.fr` ne comptent plus que pour une voix (plus de « deux écosystèmes » fabriqués par une même rédaction). Plus prudent qu'avant, aucun seuil changé. 525 tests verts ; cycle réel de contrôle : mêmes 8 noms, 0 confirmée.
* **Constat non traité** : le système classe des sources qui parlent du sujet (médias comme L'Étudiant, Le Bonbon, Valeurs actuelles ; articles Wikipédia sur d'anciens mouvements), pas des « acteurs ». Filtrer les médias demanderait une règle de Sednal (je n'invente pas de critère).

## Passerelle trouver-sites et timer 10h00 (D59, D60)

* **`sorties/resultat_tsites.csv`** (`nom;ville;pays`, UTF-8 sans BOM, mêmes 8 noms que `resultat.csv`, même tri) écrit à chaque cycle ; `resultat.csv` inchangé. `export_tsites` (actif, `pays_defaut: FR`) ajouté à `config/autonomie.yaml`. Ville : uniquement celle d'un registre officiel (commune du siège SIRENE/RNA, commune ESR, 241 domaines ESR en cache avec leur commune) ; **aucune des 8 lignes actuelles n'a de ville** (aucune n'est appariée à un registre), colonne vide, rien d'inventé. Pays : FR par défaut. 533 tests verts. Cycle réel de validation : `rapports/cycle_2026-10-11_12.md`, 0 confirmée, 8 probables, sortie conforme.
* **Timer** : quotidien à **10h00** (D60), vérifié par `systemctl --user list-timers` (prochain passage 2026-10-12 vers 10:02).
* **Q25 close (D61)** : aucun filtre, toutes les sources conservées ; la ville est un résultat de trouver-sites (jamais inventée ici, vide sans registre).

## Mission autocalibration (D62, D63, D64, D65) — en cours

Instructions de Sednal : `DECISION_AUTOCAL.md` (méthode) et `DECISION_FIABILITE.md` (ordre des étapes). Critères pré-enregistrés inchangés : `docs/CERTIFICATION.md`. Verdict : non rendu. Rapport de mesures : `docs/conception/calibration.md`.

* **Fait** : collecte réelle des 21 sujets (une seule fois) ; fournisseurs de registres (Wikidata classe + gabarit type/domaine, SIRENE/RNA par NAF ou nom) ; noms lus dans les textes (camembert-ner par défaut, wikineural en option, `config/ner.yaml`, seuil 0,93) ; variantes par nomenklatura ; indice par rapport de vraisemblance (`config/lr.yaml`, cadre ENFSI) ; profils de sortie configurables (`config/sortie.yaml`) ; périmètre des personnes préparé et **inactif** (`config/personnes.yaml`).
* **Chiffres (dev / validation, R-précision stricte, sans Wikidata)** : matin 0,020 / 0,007 -> maintenant 0,018 / 0,068 (indice non réglé). Avec Wikidata (circulaire, non probant) 0,58 / 0,92. Plafond de rappel du fournisseur de registres : 100 % de chaque liste de référence (traduction corrigée).
* **Constats ouverts** : (1) trois sujets ont des ex æquo massifs (entités SIRENE sans autre indice) : mesure sous ex æquo ajoutée ; (2) la fusion de variantes chaîne des noms sans rapport (§ 4 du rapport) ; (3) le critère 0,90 n'a de sens que sur listes fermées (§ 5) : options présentées à Sednal, rien modifié.
* **Suite** : Optuna sur dev, validation, calibration + diagramme de fiabilité, ablations, `min_ecosystemes = 1` (mesuré, jamais appliqué), intégration en production, ouverture unique du test.

## Limites connues

* Q16 à Q19 (formats Telegram, X, Instagram, web) restent ouvertes : elles se trancheront sur les premières vraies données collectées.
* L'identité d'un canal Telegram absent de `config/telegram.yaml` est une hypothèse (D33) : ses citations sont conservées mais ne valident jamais un recoupement.

## Économies de jetons

`ECONOMIES.md` (régénérable : `.venv/bin/python outils/bilan_jetons.py`) : appels routés vers le compte gratuit et gain RTK, présenté comme une estimation. Voir `docs/utilisateur.md`.

## Rapports de cycle

`rapports/cycle_<date>.md` (créés par `grappes cycle`, lisibles par un non-informaticien) ; dernier : `rapports/dernier_cycle.md`.


## Mission D62/D64 : verdict rendu (2026-10-12)

* Jeu test ouvert une fois (16:54:55 → 19:05:27 UTC) : **non certifié** (lignes A et B). R-précision stricte 0,0178 ;
  critères 1, 4c, 5 en échec ; 2, 4a, 4b, 6, 7 remplis ; 8 rapporté (+0,059). `docs/CERTIFICATION.md` § 2, D66, D67.
* Cause : 3,1 % des acteurs de la référence parmi les candidats. Test brûlé pour cette version du système.
* En attente de Sednal (non bloquant, rien n'est appliqué) : propositions du § 12 de `docs/conception/calibration.md`.
* Étape 4 (personnes) : toujours préparée seulement, collecte inactive.

## Chantiers A et B de D68 (2026-10-13)

* Chantier A : serveur MCP data.gouv.fr branché ; 4 prises YAML (`config/recherche/` : BnF, ESR, festivals et licences de
  spectacles du ministère de la Culture) lues par `decouverte/sources_yaml.py`. Mesure sur dev : 11 -> 19 acteurs de
  référence parmi les candidats (+8 sur 344), +2 063 candidats, R-précision inchangée (0,0197 contre 0,0209).
  `docs/conception/sources.md`.
* Chantier B : `traduction.lectures` + `ambiguite.json` (liste, ne départage pas).
* Classement toujours inactif par défaut ; jeu test non rouvert ; SearxNG, Overpass, expansion d'ensembles non commencés.

## D69 : cibles, vérificateur de type, amorces (2026-10-13)

* Terminé et commité (voir `docs/conception/cibles.md`, `DECISIONS.md`). Aucune phase en cours.
* Deux cibles A/B figées (`autocal/cibles.json`) ; vérificateur de type actif sur les prises (aucun acteur de référence
  perdu) ; amorces mesurées sans rien activer (gain nul avec le mécanisme mesuré, autre mécanisme à mesurer) ; prises
  data.gouv.fr mesurées sur la validation (+1 sur 281 : le gain de la mise au point ne se généralise pas).
* En attente de Sednal : thésaurus de types, mesure des amorces par requêtes web (3 crédits Tavily par sujet), nouveau
  jeu test (nouvelle graine) pour toute certification. SearxNG, Overpass, expansion d'ensembles : toujours notés, non commencés.

## Pilote (D70, 2026-10-13)

Nouvelle application `/opt/pilote` (service systemd utilisateur, `https://127.0.0.1:8443`) : Réglages, Ajout, Lancement, Tri. Suivi et
questions dans `/opt/pilote/ETAT.md` et `/opt/pilote/QUESTIONS.md`. grappes n'a gagné que le rapport d'avancement
(`GRAPPES_AVANCEMENT`). Aucune phase de grappes n'est en cours.

## Routage §4.5 corrigé (2026-10-13)

* **Diagnostic confirmé** : `outils/appeler_gratuit.sh` n'avait jamais basculé vers `sednal-free` (il journalisait puis exécutait sous l'utilisateur
  courant) et le gateway CCR n'était pas démarré.
* **Corrigé** : gateway démarré sous `sednal-free` (`ccr start --daemon --no-open`, écoute sur 127.0.0.1:3456 ; sans `--daemon` la commande reste au premier
  plan) ; `CLAUDE.md` § routage §4.5 remplacé par la commande qui bascule réellement ; le wrapper note maintenant aussi le code de sortie.
* **Bascule 1, RÉUSSIE** (18:06, 18:07) : `claude -p "dis juste OK"` sous `sednal-free` avec le modèle `OpenRouter/nvidia/nemotron-3-ultra-550b-a55b:free` répond
  « OK » (un avertissement `unrecognized_model` du client est sans effet). Preuves : le journal du gateway (`usage_events`, id 39, 14:06:27 UTC)
  montre une requête vers `openrouter::openai_chat_completions`, modèle `nvidia/nemotron-3-ultra-550b-a55b:free`, code 200, 18 539 jetons en entrée ;
  la clé OpenRouter indique `usage = 0`, `usage_daily = 0`, `limit_remaining = 50` ($0,00). Le contrôle a été fait par l'API de la clé, pas sur la page
  Activity du site (je n'ai pas accès à votre compte web) : à recouper si vous voulez la preuve visuelle.
* Suite : chaque tâche mécanique avec IA part sous `sednal-free` par le wrapper ; chaque bascule (réussie ou échouée) est notée ici et dans `donnees/.journal_ccr.log`.
* Bascule §4.5, fiche 05 (18:11) : fixture synthétique « réponse Charity Commission » produite sous `sednal-free` : **réussie** (code 0).
* Bascule §4.5, fiche 06 (18:15) : trois fixtures synthétiques (GLEIF, OpenCorporates, Pappers) produites sous `sednal-free` : **réussie** (code 0), avec une erreur de schéma à corriger à la main (clé de lien GLEIF).
* Bascule §4.5, fiche 08 (19:01) : quatre fixtures synthétiques (Overpass, Nominatim, Google Places, Google Maps/Apify) produites sous `sednal-free` : **réussie** (code 0, schémas corrects ; les coordonnées sont celles de Paris pour des noms inventés, les tests de pilote en tiennent compte). Un premier essai a échoué (code 1, 19:01:34) : le compte `sednal-free` ne peut pas lire un fichier du bac à sable de l'agent, la consigne a dû être copiée dans un fichier public temporaire (supprimé ensuite).
* **Manquement à corriger (fiche 07)** : les huit petits exemples de réponses de la fiche 07 (Telegram, Reddit, Meetup, Bluesky, Mastodon, Apify ×2, Bright Data) ont été écrits directement sur le compte Pro, sans passer par le wrapper. Du travail mécanique est donc resté sur le Pro ; à partir de la fiche 08 toute fixture passe par `sednal-free`.

## Pilote — reprise du 2026-10-17

Fiches 01 à 14 de `/opt/pilote/fiches/` traitées (suivi détaillé : `/opt/pilote/ETAT.md`, `RECETTE.md`, `QUESTIONS.md`, `BLOCAGE.md`). 08 (Lieux) et 09 (Presse) closes sous réserve (Overpass public injoignable, GDELT limité) ; 07 : emoji faits, couleur/ambiance de photo en attente d'une décision (F07-4). Pilote : 246 tests verts ; grappes non modifié ce jour (hors DECISIONS.md). Routage §4.5 : aucune fixture IA n'a été nécessaire (les scripts et jeux de test sont écrits dans les tests) ; la bascule `sednal-free` reste celle vérifiée le 13/10 (gateway actif, code 0).

## Pilote — reprise du 2026-10-19 (aucune phase de grappes en cours)

Grappes n'a pas été modifié ce jour (seulement des fichiers de suivi : rapports de cycle, journal des appels gratuits, `outils/comparer_tokens.sh`, commit `c033e6d`).
Tout le travail du jour est dans `/opt/pilote` (dernier commit `2225a29`, 327 tests verts) : deux revues complètes corrigées, sources branchées et
contrôlées en réel avec les clés de Sednal (Companies House, OpenSanctions, CourtListener, Apify),
mécanisme de vérification des candidats (`verifie_sur`), Tri avec deux signaux séparés. **Le point de reprise détaillé est à la fin de
`/opt/pilote/ETAT.md`** (commandes de redémarrage, décisions en attente F17-2 à F17-5, sources en attente de clé).
Bloquant : aucun. Routage §4.5 : les fixtures synthétiques du jour sont passées par `sednal-free` (code 0, journal `donnees/.journal_ccr.log`).

## Pilote — 2026-10-20 (aucune phase de grappes en cours)

Retrait complet d'Intelligence X (D74), retours de Sednal sur Réglages (D75) puis revue complète (D76, cinq défauts corrigés) : tout est dans
`/opt/pilote` (dernier commit `a7c2fec`, 350 tests verts ; 2 tests Wayback en échec externe, archive.org répond 429). Mesure des économies
réparée : `outils/economies.py` (ccr mesuré, rtk corrigé), rapport `docs/economies_2026-10-20.md`. Bloquant : aucun.

## Pilote — spec 905 § 1 faite (08/11/2026, aucune phase de grappes en cours)

D87 : menus fermés de `plan.js` (`RENDUS_OPTIONS`) partagés avec `reglages.js::ficheOutil()` via un nouveau
module commun `pilote/static/suite/js/options_outils.js` ; la fiche de réglage par défaut d'un outil livré
affiche désormais les mêmes vocabulaires fermés que l'éditeur de tuile, plus de champ texte libre masquant la
valeur réelle. Vérifié en navigateur réel (tool « Compteur budget ») ; 33 tests `test_suite_navigateur.py` +
`test_suite_api.py` verts, suite complète relancée (résultat à `rapports/`).
Suite de la 905 (points 2 et 3 : parité `/suite` pour l'ajout de source puis suppression de l'ancienne UI) :
non commencée, à faire dans l'ordre imposé par la spec, chaque type vérifié par Sednal sur `.60` avant le suivant.
