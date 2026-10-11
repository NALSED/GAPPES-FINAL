# ETAT — grappes

Dernière mise à jour : 2026-10-11 (Q24 close ; cycles normaux). Référence unique : `FINAL.md` (les fichiers de `docs/archive/` sont obsolètes).

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
* **À trancher par Sednal (Q25)** : écarter les articles Wikipédia de concepts ou d'événements (essai à blanc : 4 des 8 lignes). Rien n'est appliqué.

## Limites connues

* Q16 à Q19 (formats Telegram, X, Instagram, web) restent ouvertes : elles se trancheront sur les premières vraies données collectées.
* L'identité d'un canal Telegram absent de `config/telegram.yaml` est une hypothèse (D33) : ses citations sont conservées mais ne valident jamais un recoupement.

## Économies de jetons

`ECONOMIES.md` (régénérable : `.venv/bin/python outils/bilan_jetons.py`) : appels routés vers le compte gratuit et gain RTK, présenté comme une estimation. Voir `docs/utilisateur.md`.

## Rapports de cycle

`rapports/cycle_<date>.md` (créés par `grappes cycle`, lisibles par un non-informaticien) ; dernier : `rapports/dernier_cycle.md`.
