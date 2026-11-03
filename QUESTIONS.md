# QUESTIONS — grappes

Statut au 2026-10-06. Référence unique : `FINAL.md`. Aucune réponse inventée. Rien ci-dessous n'est une condition d'avancement : chaque point a une valeur par défaut documentée.

## Ouvertes (valeur par défaut en attendant)

* **Q3** Close (D82, 2026-11-03) : normalisation multilingue reste le défaut, pas de changement tant qu'aucun cas réel multilingue ne le justifie.
* **Q10** Close (D82) : client visé = agent Claude (abonnement Pro/Max), même machine que grappes (.115 production, .250 test) ; stdio/lecture seule déjà le cas, pas d'exposition réseau nécessaire.
* **Q11** Close (D82) : pas de scoring par embeddings — moins vérifiable à l'œil que le lexique, rien ne montre que le lexique rate des recoupements ; à revoir seulement si un cas réel le montre.

* **Q20** Close (D82) : le garde-fou reste actif par défaut, mais c'était déjà un réglage réel (`autonomie.yaml: apprentissage.exiger_racine_de_confiance`, chargé par `autonomy.py`) — confirmé, rien à coder.
* **Q21** Close (D82) : remplacé par un critère de correspondance en trois cas (matche directement / hors sujet / doute → `resultat_a_trancher.csv`), pas une exclusion de principe. Détail et code : D82, `clustering/resultat.py`.

* **Q28** Close (D83, 2026-11-03) : réutilise le mécanisme d'ancre déjà existant (`anchors:` du YAML de la grappe). `resultat_a_trancher.csv` (NOM, GRAPPE, REF, DECISION) + `grappes ancrer` promeut chaque ligne « garder » en ancre. Détail et code : D83, `ancrage.py`.

* **Q22** Réglée (D46) : écosystèmes `rss` et `wikipedia` ajoutés comme fournisseurs. Voir Q24 pour ce qui reste.
* **Q23** Réglée (D47) : nouveau sujet, `seuil_ingestion` auto-ajustable dans [5 ; 40].
* **Q24** Close (acceptée, D56) : « probable » est le niveau maximal pour le sujet actuel ; D50 à D55 restent en place pour plus tard.

## À trancher sur les premières vraies données collectées (Q16 à Q19)

Aucun export n'est attendu de Sednal (`FINAL.md` § 3) : ces points se tranchent sur les premières données réellement ramenées par la collecte, quelle qu'en soit l'origine. Les formats actuels viennent d'échantillons construits d'après les documentations officielles ; aucun champ n'a été supposé au-delà (détail dans `docs/conception/formats_json.md`).

* **Q16** Telegram (export Desktop) :
  * l'URL d'un `text_link` est-elle bien dans `href` ? L'échantillon n'en contient pas ; le fetcher lit `href`, à défaut `url` ;
  * champs des messages de service (`action`, `actor`...) : ils sont seulement ignorés ; certains portent-ils une information utile (ajout de membres, épinglage) ?
  * l'export ne donne que le nom affiché du canal (`name`), pas son nom public : l'identifiant vient de la table d'équivalence de configuration (D25, référence), à défaut du nom mis en forme, marqué « hypothèse ». Existe-t-il un champ de nom public dans les vrais exports ?
  * `forwarded_from` est un nom affiché (pas d'identifiant) : même heuristique ;
  * `date` sans fuseau : `date_unixtime` (UTC) est préféré, est-ce toujours cohérent ?
  * export d'un groupe ou d'un compte complet (`chats.list`) : la structure diffère-t-elle ? Aujourd'hui seul `{name, messages}` est géré, et la source reste le chat, jamais l'auteur du message.
* **Q17** X (API v2) :
  * les mentions portent-elles toujours `username` en plus de `id` ? Sans `username`, résolution par `includes.users` si possible, sinon la mention est ignorée ;
  * `includes.users` est-il toujours présent ? Sans lui, aucun auteur n'est résolu et le tweet est rejeté ;
  * faut-il compter `referenced_tweets` (retweet, citation, réponse) et `in_reply_to_user_id` comme des citations ? Aujourd'hui seules les mentions et les liens citent ;
  * `engagement` = like + retweet + reply (quote, bookmark, impression exclus) : à valider.
* **Q18** Instagram (API Graph) :
  * `username` est-il toujours renvoyé par la liste de médias ? Sans lui, le média est rejeté ;
  * structure de `paging` (`cursors`, `next`) : ignorée, la collecte et le suivi des pages restent hors périmètre ; faut-il les gérer ?
  * les noms d'utilisateur peuvent contenir un point : le motif de mention actuel (`@\w+`) s'arrêterait au point ;
  * légende, mentions et hashtags n'ont pas d'entités structurées : extraction par expression régulière ;
  * les commentaires et `children` (carrousels) sont ignorés.
* **Q19** Web (partiellement confirmée le 2026-10-11, voir `ETAT.md`) : le format d'entrée est une proposition de Sednal (aucun standard). `published_at` préféré à `fetched_at`, `canonical_url` préférée à `url`, `links[].anchor` ignoré. Format réel du collecteur à fournir.

## Réglées ou provisoires

* **Q7** Cadre de données : valeurs proposées par Claude (D30) — sources publiques seulement, `retention_days` 90, `redact_persons` actif, personnes physiques exclues de `resultat.csv` — réversibles par Sednal ; elles remplacent D20 et D21.
* **Q15** Réglée (D19) : E vaut 0 tant que le recoupement n'est pas validé ; `explain` indique `recoupement_partiel`.
* **Q1** Réglée : « grappes » reste le nom de travail.
* **Q4, Q5, Q9** Valeurs actuelles gardées (seuils par défaut ; CSV `;`, UTF-8 sans BOM ; règle d'opposition par marge). Provisoire, à recalibrer avec des données réelles.
* **Q6** Thèmes neutres de démonstration conservés (jeux d'essai ; les vraies grappes viennent des sujets).
* **Q8** Sans objet (plage horaire supprimée).
* **Q12** Réglée : hook `Stop` migré et vérifié.
* **Q13** Pas de watchdog pour l'instant (D4 reste « proposée »). Chaque interruption « session limit » est notée dans `ETAT.md`.
* **Q14** Classification mécanique / jugement validée ; N = 5, atteint (8 lignes dans le journal).
* **QA** Confirmé : on suit `MISSION.md` (`grappes`).
* **QB** Réglée : hook `Stop` vers `/opt/grappes/outils/continuer.sh`.
* Corrections de `MISSION.md` (dont les Q12 à Q19 manquantes du §17) : proposées dans `docs/conception/corrections_mission.md` ; `MISSION.md` n'est pas modifié.
* **Q25** Close (D61) : aucun filtre, on garde toutes les sources ; ville = résultat de trouver-sites. Énoncé d'origine : Distinguer, dans les sorties, les articles Wikipédia d'**organisations** de ceux de **concepts ou d'événements** (trouver-sites ne peut rien trouver pour ces derniers). Faisabilité : oui, avec les catégories Wikipédia déjà lues à l'ingestion (elles servent à écarter les personnes), mais elles ne sont pas conservées en base : il faudrait les stocker. Essai à blanc sur le jeu actuel (catégories lues le 2026-10-11, 5 articles) : 4 lignes sur les 8 de `resultat.csv` seraient écartées (« Mouvements étudiants en France », « Mouvements lycéens », « Mouvement contre le contrat première embauche de 2006 », « Mouvement lycéen et étudiant de 2026 en France » : catégories « Mouvement social… », « Mouvement étudiant », « Manifestation en… », « Conflit social… », « Grève étudiante »), 1 conservée (« Union nationale des étudiants de France » : « Syndicat étudiant en France », « Organisation étudiante représentative », « Association… »). Les 3 lignes de sites web (L'Étudiant, Le Bonbon, Valeurs actuelles) ne sont pas concernées. Réserve : la règle repose sur deux listes de préfixes de catégories (événement/mouvement d'un côté, organisation de l'autre), donc sur un critère à valider ; sur d'autres sujets elle pourrait écarter à tort (ex. un mouvement qui est aussi une organisation). Si accord : filtre appliqué seulement à `resultat_tsites.csv`, ou aussi à `resultat.csv` (à préciser).

## Q26 — Autocalibration : plafond de rappel de 0 à 17 % (2026-10-12) — Close (D82, 2026-11-03)

Sur dev et validation, au plus 17 % de la référence Wikidata existe comme candidat vérifié « juste » (12 sujets mesurés) ; R-précision stricte observée 0,020 / 0,007, identique pour tous les algorithmes. Le seuil 0,90 du critère 1 est inatteignable avec des entités = sources. Pistes à chiffrer avant tout gel (rien n'est appliqué) : (a) crawl plus grand, (b) extraction d'entités nommées dans les textes lus (hors liste des méthodes de la mission, donc à décider par Sednal), (c) nom lisible des domaines. Sans changement d'architecture, le verdict sera « non certifié ».

Mesures complémentaires (2026-10-12) : (1) trois cycles de collecte successifs sur handball-pro et sur g-q56199177 (réseau réel) ne changent rien : 21 puis 37 candidats, plafond de rappel inchangé (5,9 % et 17,4 %) ; le crawl plus long ne relève pas le plafond. (2) `min_ecosystemes = 1` (autonomie, apprentissage des termes) rejoué sur les 12 sujets de dev et validation : mêmes candidats, mêmes « justes » ; aucun effet mesurable sur un cycle. Rapporté, non appliqué. (3) Un classement parfait plafonne la R-précision stricte à ≤ 0,17 ; atteindre 0,90 suppose que les ACTEURS (organisations nommées dans les textes) soient les candidats, pas les sources.

**Décision (D82)** : Sednal autorise l'extraction (b), sa seule utilité étant pour un mode de recherche précis (une recherche qui cible directement des sites/comptes n'a rien à en extraire). Nouveau réglage **`scoring.mode_recherche`**, deux valeurs fermées : `sites` (défaut, comportement actuel) ou `extraction` (lit le contenu, les acteurs nommés deviennent candidats de recoupement). Réutilise le classement de production déjà mesuré (D63-D65) plutôt que d'inventer un nouveau mécanisme. Code et tests : `config.py`, `classement/production.py::cc_pour_mode`, `tests/test_phase4.py`, `tests/test_classement_production.py`. Le gain de rappel réel (le chiffrage du plafond avec extraction activée) reste à mesurer sur un vrai cycle réseau, hors de ce sandbox.

## Q27 — D69 : trois décisions qui reviennent à Sednal (2026-10-13) — Close (D82, 2026-11-03)

Détail et chiffres : `docs/conception/cibles.md` §§ 4, 5 et 7.

* **Thésaurus de types** : décision (D82) : rattachement au code NAF officiel (INSEE) ↔ classe plutôt qu'une liste de synonymes inventée — nomenclature déjà existante et autoritaire. **Pas encore codé.**
* **Amorces par requêtes web** : mesure du mécanisme TREC autorisée par Sednal (~3 crédits Tavily/sujet), décision d'implémentation seulement après ce chiffrage. **Pas lancée ici** : coûte des crédits réels, à faire dans une session dédiée avec le budget alloué.
* **Nouveau jeu test** : confirmé nécessaire avant toute certification ; à geler juste avant la prochaine tentative, pas avant si aucune n'est encore visée. **Pas fait.**

## Revue complète du 03/11/2026 (spec `902`, D84)

Demandée par Sednal avant 1.3 et l'« après le pavé », sur le modèle de D76. Périmètre : tout ce que la session
a livré (T1/T2/T4, 1.1, 1.2, 3.3, 3.4, 3.6, 3.7, 3.8.01 à 3.8.10, 901/D82-D83). Note de numérotation : la spec
902 parle de « D82-D84 » — c'était la numérotation d'une autre session, poussée puis annulée (`b758fb3`/`33bdbb1`) ;
ici 901 = D82, Q28 = D83, cette revue = D84.

### Tests (détail, pas seulement le compte)

* **grappes** : 612 tests, tous verts (dont 3 nouveaux de cette revue).
* **pilote, `-m "not reseau"`** : avec la configuration livrée, 27 échecs + 5 erreurs, **tous** dus à
  `grappes.racine: ../grappes`, qui n'existe pas dans ce dépôt (le moteur est la racine) — c'est le §3 de `900`,
  non touché. Avec cette seule ligne corrigée **localement, jamais commitée** (`racine: ..`) : **563 réussis,
  1 échec** après les corrections de cette revue (557 + 2 au premier passage), détaillés ici :
  1. `test_squelette.py::test_configuration_livree_est_lisible` — vérifie à la fois `racine: ../grappes` et qu'on y
     trouve la configuration du moteur : il échoue donc dans les deux cas (avec la configuration livrée, il fait
     partie des 27). Il devra changer avec `900` §3.
  2. (premier passage seulement) `test_verrou_des_sauts.py::test_les_assistants_qui_sautent_sont_connus` —
     préexistant, venu de l'import de GRAPPES : la fixture autouse `_exige_pytrec_eval` peut faire sauter `test_mesurer_classement.py` sans marque
     `reseau`, contre la règle « `-m "not reseau"` ne saute jamais ». **Corrigé** (marque `reseau` au module,
     assistant déclaré au garde).
  3. Au deuxième passage, trois échecs dus à mes propres corrections, repris aussitôt : deux tests d'export qui
     attendaient l'ancienne liste de colonnes, et un test IA qui a révélé le tirage au hasard de la tuile jouée
     (voir plus bas).
* **pilote, tests navigateur** (`tests/test_suite_navigateur.py`, marqués `reseau`) : 13 réussis, dont l'ouverture
  des dix fiches outils (nouveau menu Effort compris) et les gardes de charte (vocabulaire fermé, aucune valeur de
  style en dur). Les autres tests `reseau` (services extérieurs réels, bases de données jetables) n'ont pas été
  lancés.

### Défauts trouvés, par gravité

**Bloquant — corrigé**

* **3.8.09** : toute recherche avec une tuile Assistant IA finissait en **échec** (« 'resume_ia' is an invalid
  keyword argument for Candidat ») : le champ IA était posé en colonne de la fiche, que la base ne connaît pas.
  Invisible aux tests unitaires, trouvé par le test réel. Le texte IA va maintenant dans `faits["ia"]`, la marque
  dans `faits["ia_marque"]` (la donnée IA ne se mêle jamais aux faits trouvés, spécification 10 règle 1). Test de
  non-régression : `test_le_candidat_accepte_une_ligne_traitee_par_l_ia`.

**Majeur — corrigé**

* **3.8.09, écarts à la spec** : l'IA passait après la vérification (spec : après les chemins, avant la
  vérification) ; elle traitait tous les noms (spec : ceux qui atteignent la tuile) ; aucun refus à la
  compilation sans agent (spec : « refuse de s'appliquer et le dit ») ; pas de champ Effort alors que
  `claude --effort` existe (spec : l'ajouter dans ce cas). Plus deux défauts : la boucle IA ignorait l'arrêt
  demandé et la limite de temps ; et sous un service systemd (`pilote.service`), le PATH ne contient pas
  `~/.local/bin`, où s'installe l'agent — chaque appel aurait échoué sur .115. Tout corrigé et testé.
* **3.8.09, export** : aucune colonne pour ce que produit l'IA → colonne `ia` dans les exports détaillés,
  préfixée « [IA] » quand la tuile marque ses résultats.
* **Q26 (D82, moteur)** : le mode `extraction` activait aussi les **registres**, contrairement à Q26 (qui ne
  demande que l'extraction des textes lus) et à ce que j'avais écrit dans D82. En conditions réelles : onze
  organisations sans rapport (« L'Acteur rural », « Colloque sur la formation de l'acteur »…) venues du registre
  BnF, qui avait pris « acteurs » au pied de la lettre. Corrigé : extraction seule.
* **Moteur (préexistant, hors session)** : une page dont l'adresse contient des accents était perdue sur
  `UnicodeEncodeError` (3 pages d'un média au cycle réel). Corrigé à l'envoi seulement (accents en `%xx`, domaine
  en IDNA) ; l'adresse gardée ne change pas. Vérifié en réel : la page perdue répond (200).

* **Plan de travail (préexistant)** : l'ordre des outils venait d'un ensemble Python, dont l'ordre change d'un
  processus à l'autre. « Une seule tuile jouée, les suivantes ignorées » (Fusion / doublons, Attente, Assistant IA)
  désignait donc **une tuile au hasard** d'un lancement à l'autre (mesuré : 1 graine sur 6 choisissait l'autre).
  Corrigé : ordre du plan. Test : `test_la_tuile_jouee_ne_depend_pas_du_hasard_du_processus` (six graines).

**Mineur — corrigé**

* **Q28** : `grappes ancrer` répondait « grappe introuvable » sur une grappe issue d'un sujet → message explicite
  (voir Q29).

**Observation (non corrigée, préexistante)** : `grappes cycle` et `grappes export` écrivent une partie de leurs
fichiers relativement au dossier courant, quels que soient `--config`/`--db`/`--out` (rapport dans `rapports/`, caches
dans `donnees/`). Mon test en copie isolée a donc écrit dans le dépôt réel ; rangé à la main (rapport et caches
déplacés, `dernier_cycle.md` remis comme avant). À garder en tête pour tout test en copie.

**Écarts à la spec non corrigés (pas routiniers) — à reprendre**

* ~~**3.8.10 RSSHub**~~ — **fait juste après la revue (D85)** : instance déployée sur .250 (Docker, boucle locale
  seulement), contrat réel vérifié (règles Radar), flux suivi comme un flux ajouté à la main, plus de duplication
  avec `flux_rss`. Détail : `pilote/QUESTIONS.md` § 3.8.10.
* **3.8.04 Boucle** : la spec demandait le mécanisme multi-tours dans `ExecuteurGrappes` ; non fait (raisons dans
  `pilote/QUESTIONS.md`). Maintenant que la suite pilote tourne contre le vrai moteur ici, la vérification devient
  possible ; reste l'ambiguïté du garde-fou « tours × appels > budget » (quel budget ?).
* **3.8.08** : budget propre à une recherche non branché (`NON_APPLIQUES["budget"]`) — la spec le permet
  (« sinon, seul le renommage crédit est fait ici »), mais ses critères de vérification (arrêt à 20 % du plafond)
  ne sont donc pas tenus.
* **3.8.09** : « Modèle » reste un champ libre (aucune liste interrogeable, vérifié) ; les options propres aux
  opérations (`catégories` pour Classer, `maximum` pour Extraire) ne sont pas exposées dans la tuile.

### Questions pour Sednal

* **Q29** — Ancrage (Q28) et configuration réelle : la seule grappe vient de `sujets.yaml`, qui n'a **pas** de liste
  `anchors:` (seules les grappes `config/grappes/*.yaml` en ont). `grappes ancrer` ne peut donc rien écrire en
  production. Où ranger les ancres d'un sujet : (a) une liste `ancres:` par sujet dans `sujets.yaml`, (b) un fichier
  d'ancres à part par grappe, (c) autre ? Défaut en attendant : refus explicite, rien d'écrit.
* **Q30** — Q26 côté pilote : le pont de pilote **extrait les noms à chaque recherche depuis toujours**
  (`classement.yaml: noms: true`, modèle installé). La prémisse de 901 (« comportement actuel = aucune
  extraction ») est donc fausse pour pilote. Appliquer « jamais en dehors du second mode » à pilote retirerait les
  noms lus de toutes ses recherches par défaut. Et le mode n'a aucun écran : c'est un réglage global du moteur
  (`scoring.yaml`). Faut-il : un choix par recherche dans pilote (simple/avancée) ? Quel défaut pour pilote ?
* **Q31** — Q21 côté pilote : la règle à trois cas ne vaut que pour `resultat.csv` du moteur. pilote a son propre
  mécanisme (règle n° 8 : fiche « personne », hors rapprochements et FollowTheMoney, levée fiche par fiche dans
  Tri) où les personnes restent visibles. Aligner les deux ? Par ailleurs Q21 **n'est pas observable en réel** : le
  moteur ne lit jamais un compte de réseau social (« citation seulement, jamais lu »), aucune personne n'atteint
  `resultat.csv` par les sources réelles.
* **Q32** — Interface : 901 (« Consigne d'interface ») et 902 (§2) parlent d'éléments d'écran pour le mode de
  recherche et le fichier « à trancher ». Ils **n'existent pas** : j'ai livré réglage + mécanisme, sans écran. À
  construire ? Où (Réglages, Recherche, Tri) ?
* **Q33** — `/api/suite/lancer` n'a pas de « combien » : une tuile IA peut traiter jusqu'à 200 noms (≈ 5-10 s
  chacun avec l'agent). L'arrêt et la limite de temps sont maintenant respectés ; faut-il en plus un plafond de
  noms traités par l'IA ?
* **Q34** — `900` §3 (une ligne : `grappes.racine: ..`) : c'est la seule raison des 27 échecs + 5 erreurs de pilote
  dans ce dépôt, et sans elle pilote ne peut lancer aucune recherche réelle depuis GAPPES-FINAL. La faire
  maintenant, avant le reste de `900` ?

### Test en conditions réelles

* **Moteur**, copie isolée (configuration, base, sorties, journal à part ; l'état réel de la mission n'est pas
  touché), sujet réel « Les acteurs des blocages et mobilisations étudiantes en France en ce moment » : 9 requêtes
  Tavily, 158 résultats examinés, 27 observations. Mode `sites` : 7 noms, surtout des articles et événements
  Wikipédia, **aucun acteur**. Même base, mode `extraction` (sans registres) : 27 noms, dont les acteurs attendus
  — UNEF, CGT, FAGE, Union étudiante, Union syndicale lycéenne, Interfac — et du bruit propre à l'extraction
  (G20, BHV, Banque de France, « ministre de l'Intérieur » : nommés dans les mêmes articles). Exploitable : le mode
  fait ce que Q26 annonçait, au prix d'un tri.
* **pilote**, configuration isolée, vraie source gratuite (Registre des associations) + Filtre « garder au maximum
  5 » + Assistant IA « Résumer » (modèle `haiku`) : recherche terminée en 28 s, 3 résumés réels, marqués,
  exportés « [IA] … », compteur au journal (`plan_ia_appels`) et compteur de tuile. Qualité : sur des fiches de
  registre sans texte, le résumé ne fait que reformuler les métadonnées — l'opération sera utile surtout sur de la
  presse. Le registre lui-même a rendu 2 résultats sur 3 hors sujet (UCPA) pour « fédération des associations
  générales étudiantes ».
