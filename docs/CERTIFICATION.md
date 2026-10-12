# CERTIFICATION — score continu, classement et volume (mission D62)

Ce document porte le **verdict** de la mission `DECISION_AUTOCAL.md`. Il est écrit en deux temps : les critères sont
**pré-enregistrés** ci-dessous (avant toute mesure sur le jeu de test) ; le verdict est ajouté à la suite, sans
toucher aux critères. Déplacer un critère après avoir vu les résultats annule la certification.

Verdict : **NON CERTIFIÉ** (ligne A, qui fait foi) ; la ligne B (listes fermées) est elle aussi **non certifiée**. Détail au § 2.

## 1. Pré-enregistrement (figé le 2026-10-12 vers 06:10 UTC, avant la collecte des sujets et avant tout test)

Jeux de sujets : `autocal/jeux.json` (graine 20261012, empreinte SHA-256 tronquée `f318b652560c58ba` au moment du
figement). Le jeu **test** est ouvert **une seule fois**, paramètres figés, date et heure consignées dans
`autocal/test_ouvert.json` ; toute seconde ouverture le « brûle » et le dit dans le verdict.

Définitions communes.

* Référence = silver standard Wikidata (supervision distante), jamais une vérité absolue. Trois comptes : juste, faux,
  non vérifiable. **Un non vérifiable ne compte jamais comme juste** : toutes les R-précisions ci-dessous sont
  « strictes » (document non jugé = non pertinent, réglage par défaut de `trec_eval`).
* « Sujets positifs du jeu test » : les six sujets non témoins ; « témoin » : le sujet sans acteur réel.
* Seuil de confiance haute : **τ = 0,90** (probabilité calibrée, étiquette stricte juste / non juste).
* Les fournisseurs Wikipédia, Wikidata et dérivés (wikipedia.org, wikidata.org, wikimedia.org, wikiwand.com,
  dbpedia.org) sont exclus de toute collecte d'évaluation (non-circularité).

Critères (tous requis pour « certifié »).

| N° | Critère | Seuil figé |
|---|---|---|
| 1 | R-précision stricte, moyenne des sujets positifs du jeu test | ≥ 0,90 ; bpref rapporté à côté |
| 2 | Volume : pour chaque sujet test dont R est dans [20 ; 200], le nombre rendu quand on demande N = R tombe dans [0,9 R ; 1,1 R] | vrai pour au moins 80 % de ces sujets ; le taux de remplissage pour N ∈ {20, 50, 100, 200} est rapporté |
| 3 | Sujets difficiles | mesurés et rapportés à part (R-précision, bpref, trois comptes), sans seuil, même mauvais |
| 4 | Contrôle négatif et permutation | (a) sur le témoin du jeu test, aucun résultat à p calibrée ≥ τ ; (b) sur les sujets positifs du jeu test, aucun résultat **faux** (vérifié) à p calibrée ≥ τ ; (c) test de permutation (1 000 permutations des jugements parmi les candidats, graine fixée) : la R-précision permutée moyenne ne dépasse pas le hasard R/n + 0,05, et la valeur observée dépasse le 95e centile des permutations pour au moins 80 % des sujets positifs |
| 5 | Calibration (jeu test, étiquette stricte, 10 intervalles de largeur égale) | ECE ≤ 0,10 et score de Brier inférieur à celui du prédicteur constant (taux de base) ; diagramme de fiabilité fourni |
| 6 | Reproductibilité | deux rejeux, mêmes données et mêmes paramètres : fichiers de résultats identiques octet pour octet |
| 7 | Aucune régression | la suite `pytest` existante reste entièrement verte |
| 8 | Écart d'optimisme | rapporté : (score de validation) − (score de test) en R-précision ; pas de seuil |

Comparaisons obligatoires, données à côté de chaque chiffre : le système avant la mission (`actuel`), le vote
majoritaire (`vote`), et chaque ingrédient retiré à tour de rôle (étude d'ablation).

Remontés sans application (AUTONOMIE) : mesure de `min_ecosystemes = 1` (rapportée, jamais appliquée) ; tout
changement de format de `resultat.csv` ; toute suppression de données collectées.

### 1 bis. Addendum du 2026-10-12 (décision de Sednal : option 2), AVANT toute ouverture du jeu test

Sednal a choisi d'ajouter une **seconde ligne de verdict**, présentée **à côté** de la première sans la remplacer.
Les critères 1 à 8 et leurs seuils ci-dessus restent **inchangés** ; seul l'ensemble de sujets sur lequel on les lit
diffère.

* **Ligne A (principale, inchangée)** : les six sujets positifs du jeu test.
* **Ligne B (complémentaire)** : les seuls sujets positifs du test à « liste fermée ». Règle **fixée ici avant
  ouverture**, jugée sur la **seule phrase** du sujet, jamais sur un résultat : la liste est fermée quand l'ensemble
  désigné est arrêté par une autorité publique (labellisation, classement officiel), donc fini et énumérable. Pour le
  test : « Pôle de compétitivité en France » (g-q3412193) et « Conservatoire à rayonnement régional en France »
  (g-q17487523) ; les quatre autres (bibliothèque universitaire, groupe de pression, brasserie, ensemble musical)
  sont ouverts. Liste figée dans `autocal/ligne_b.json`. *(Un calcul R/T contre le total SIRENE/RNA a été essayé le même
  jour, avant ouverture, puis écarté : il confond « le registre ne connaît pas le sujet » et « la liste est complète »,
  par exemple bibliothèques numériques R = 45, T = 1 sur le jeu de mise au point.)* Limite annoncée : la règle ne
  garantit pas que R soit complète ; la part de l'effectif officiel couverte par R est constatée et rapportée au verdict.
* Sur la ligne B, le critère 1 (R-précision stricte moyenne >= 0,90) est lu sur ce sous-ensemble ; les critères 2 à 8
  sont les mêmes qu'en ligne A (ils ne dépendent pas du choix du sous-ensemble) ; la ligne B est « certifié » seulement
  si les huit sont remplis. Les deux lignes sont rendues, jamais fusionnées ; la ligne A fait foi pour « certifié ».
* Probabilité calibrée utilisée par les critères 4 et 5 : la sigmoïde de Platt ajustée sur dev + validation (sans
  Wikidata) et figée dans `config/calibration.json` (`ajustement_platt_non_valide`, a = 1,0993, b = −4,3049). Elle est
  déclarée « non valide » (pas de pouvoir discriminant mesuré en validation) : le verdict le dira, il ne la remplace pas.
* Système mesuré : paramètres Optuna de `autocal/resultats/etape3_optuna.json` (= `config/lr.yaml`), registres
  [sirene], noms lus (`config/ner.yaml`, seuil 0,93), Wikidata désactivé, variantes désactivées, N maximal 200.
* Mécanisme d'ouverture unique : `python -m grappes.autocal.test_final`. Il écrit `autocal/test_ouvert.json` (date,
  heure UTC, empreintes des paramètres et des critères) **avant** de lire quoi que ce soit du test ; une seconde
  exécution est refusée et consignée dans `reouvertures`, ce qui « brûle » le test et doit figurer dans le verdict.

## 2. Verdict

Jeu test ouvert **une seule fois** : début **2026-10-12 16:54:55 UTC**, fin 19:05:27 UTC, code au commit `51a4ae1`
(empreintes des paramètres dans `autocal/test_ouvert.json`, aucune réouverture). Résultats complets :
`autocal/resultats/test_final.json` ; diagramme de fiabilité : `docs/conception/fiabilite_test.png`. Système mesuré :
paramètres Optuna figés, SIRENE/RNA + noms lus (seuil 0,93), Wikidata désactivé, variantes désactivées, calibration
de Platt figée (« non valide », voir plus bas).

**Verdict ligne A (six sujets positifs du test) : NON CERTIFIÉ.** Trois critères sur huit ne sont pas remplis (1, 4c, 5).
**Ligne B (listes fermées par définition : pôle de compétitivité, conservatoire à rayonnement régional) : NON CERTIFIÉE**
(mêmes critères 4c et 5 en échec, critère 1 à 0,033).

### 2.1 Critère par critère

| N° | Critère | Mesure sur le test | Résultat |
|---|---|---|---|
| 1 | R-précision stricte moyenne >= 0,90 | **0,0178** (bpref 0,0184) ; ligne B : 0,0326 | **NON REMPLI** |
| 2 | Volume N = R dans [0,9 R ; 1,1 R] pour >= 80 % des sujets | 6 sujets sur 6 (taux 100 %) ; remplissage N = 20 / 50 / 100 / 200 : 100 % / 100 % / 100 % / 100 % | rempli (voir réserve) |
| 3 | Sujets difficiles, à part, sans seuil | tableau § 2.2 | rapporté |
| 4a | Témoin : aucun résultat à p calibrée >= 0,90 | p maximale du témoin 0,34 | rempli |
| 4b | Aucun faux vérifié à p >= 0,90 | 0 (p maximale de tout le test : 0,44) | rempli |
| 4c | Permutation (1 000, graine 62) : permutée <= R/n + 0,05 ET observée > 95e centile pour >= 80 % des sujets | permutée moyenne 0,0062 (borne 0,2856) : rempli ; observée > p95 pour **1 sujet sur 6** (17 %, seuil 80 %) | **NON REMPLI** |
| 5 | ECE <= 0,10 ET Brier < prédicteur constant | ECE 0,0105 (rempli) ; **Brier 0,00680 contre 0,00651** pour le prédicteur constant (11 justes sur 1 679) | **NON REMPLI** |
| 6 | Deux rejeux identiques octet pour octet | identiques (empreinte SHA-256 tronquée dans le journal) | rempli |
| 7 | `pytest` tout vert | 571 passés | rempli |
| 8 | Écart d'optimisme (rapporté) | validation 0,0768 − test 0,0178 = **+0,0590** | rapporté |

*Réserve sur le critère 2* : il est rempli de façon **mécanique**. Le système rend toujours au moins 200 candidats, donc
le volume demandé est toujours servi, mais 70 à 90 % de ce qui est servi est faux ou non vérifiable (§ 2.3). Le volume
n'a pas de valeur sans la précision.

### 2.2 Sujets difficiles (critère 3) et comptes, sans seuil

| sujet | difficulté déclarée | R | candidats | R-préc. stricte | bpref | juste / faux / non vérifiable (tous candidats) | justes dans les R premiers |
|---|---|---|---|---|---|---|---|
| g-q3412193 pôle de compétitivité | facile | 22 | 316 | 0,000 | 0,000 | 0 / 143 / 173 | 0 |
| g-q17487523 conservatoire à rayonnement régional | facile | 46 | 245 | 0,065 | 0,064 | 3 / 95 / 147 | 3 |
| g-q856234 bibliothèque universitaire | moyen | 117 | 209 | 0,000 | 0,0002 | 2 / 78 / 129 | 0 |
| g-q1666019 groupe de pression | moyen | 60 | 213 | 0,000 | 0,000 | 0 / 109 / 100 | 0 |
| g-q131734 brasserie | difficile | 72 | 367 | 0,042 | 0,046 | 6 / 116 / 245 | 3 |
| g-q2088357 ensemble musical | difficile | 39 | 329 | 0,000 | 0,000 | 0 / 75 / 254 | 0 |

Le témoin (écoles de sorcellerie de Haute-Savoie) rend 168 candidats, tous de p calibrée <= 0,34 : il ne fait pas
d'acteur réel, mais l'indice ne le sépare pas non plus nettement des sujets réels (p maximale 0,44).

### 2.3 Cause du résultat, mesurée (aucune interprétation nouvelle sans chiffre)

* **Le rappel des candidats plafonne tout.** Sur les six sujets, **11 acteurs de la référence sur 356 (3,1 %)** figurent
  parmi les candidats, tous classements confondus. Même un classement parfait des candidats existants ne pourrait pas
  dépasser une R-précision d'environ 0,03. Le même plafond avait été mesuré le matin du 2026-10-12 (0 à 17 % selon le
  sujet) : le défaut est dans **ce que la collecte et les sources fournissent**, pas dans l'ordre du classement.
* **Les registres sans Wikidata n'apportent rien sur ces sujets** : le total SIRENE/RNA est de 2 à 14 établissements pour
  quatre sujets (6, 14, 8, 2), 113 et 200 pour les deux autres (ensemble musical, brasserie : populations immenses où la
  référence est une toute petite partie). « Sans SIRENE/RNA » donne exactement le même 0,0178.
* **Ingrédients retirés (R-précision stricte, test)** : complet 0,0178 ; sans SIRENE 0,0178 ; sans noms lus 0,0160 ;
  sans proximité du texte propre 0,0133 ; sans écosystèmes 0,0178 ; sans citations 0,0178 ; web seul 0,0146 ;
  système d'avant (`actuel`) 0,0146 ; vote majoritaire 0,0146. Le système réglé fait mieux que le système d'avant sur le
  test (0,0178 contre 0,0146), mais de moins d'un demi-point : **dans le bruit**, avec 11 justes en tout.
* **Les noms lus, qui avaient fait passer la validation de 0,007 à 0,077, n'ont pas reproduit ce gain sur le test**
  (0,0160 sans, 0,0178 avec). L'essentiel du gain de validation venait du seul sujet cac40 (0,35), liste fermée de 40 noms
  connus. C'est l'écart d'optimisme du critère 8 : +0,059 en faveur de la validation, qui n'était pas représentative.
* **La calibration ne discrimine pas** : avec 11 justes sur 1 679, la sigmoïde de Platt ajustée sur dev + validation
  donne une ECE correcte (0,0105) parce que toutes les probabilités sont petites (p maximale 0,44), mais un Brier **plus
  mauvais que le taux de base**. C'est le résultat annoncé en validation (0,0234 contre 0,0229), confirmé en test. Aucun
  résultat n'atteint p >= 0,90 : le système n'en affirme aucun avec confiance, c'est cohérent et honnête, mais cela ne
  répond pas au critère de fiabilité.

### 2.4 Hypothèses de Sednal contredites ou non confirmées par la mesure

* **« La traduction du sujet en requête est le gain le plus rentable » (point 2)** : confirmée sur les sujets dont la
  classe vient de Wikidata (circulaire), **non démontrée** sur des sujets dont la référence est indépendante : sans
  Wikidata, les registres SIRENE/RNA n'ajoutent rien au test.
* **« Une source de plus (les noms lus) change le rappel » (Q26, étape 2)** : vraie sur validation (cac40), non
  reproduite sur le test (+0,002).
* **« Des acteurs plus nombreux seraient trouvés en élargissant la collecte » (point 6, repoussé)** : non testée ici ;
  le plafond de 3,1 % de rappel des candidats dit seulement que l'élargissement serait le levier à mesurer en premier.

### 2.5 Ce qu'il manque, tentative, chiffre, explication, proposition

| critère manquant | tentative | chiffre | explication | proposition (à Sednal, rien n'est décidé ni appliqué) |
|---|---|---|---|---|
| 1 | traduction en requêtes de registre, noms lus, indice réglé par Optuna (108 essais), calibration | 0,0178 (ligne B 0,0326) | rappel des candidats 3,1 % : les acteurs de la référence ne sont presque jamais parmi les candidats | (a) remettre Wikidata comme fournisseur de **découverte** en production avec l'étiquette « estimation étendue » (hors de la zone mesurable, car circulaire) ; (b) construire une référence indépendante d'un registre pour mesurer SIRENE/RNA sans circularité (option 4 du § 5 de `calibration.md`) ; (c) mesurer un élargissement de la collecte web (point 6) sur les sujets de mise au point d'abord |
| 4c | l'indice classe au-dessus du hasard sur 1 sujet (conservatoires) | 1 sur 6 > p95 | 4 sujets sur 6 ont zéro juste : observée = permutée = 0, ce qui ne dépasse pas le 95e centile | même cause que le critère 1 ; ne se corrige qu'en trouvant plus d'acteurs réels |
| 5 | Platt et isotone, ajustées en dev + validation | Brier 0,00680 > 0,00651 | 11 justes seulement : aucun signal à calibrer | même cause ; à re-mesurer après (a) ou (c) |

### 2.6 Statut des décisions pendantes

* Le jeu test est **brûlé** pour cette version du système : toute nouvelle mesure sur ces six sujets n'a plus de valeur
  de certification. Une certification ultérieure demandera un **nouveau jeu test** tiré avec une nouvelle graine, fixé
  avant toute modification du système.
* `min_ecosystemes` reste à 2 (mesure de la valeur 1 rapportée au § 9 de `docs/conception/calibration.md`, non appliquée).
* Aucune donnée collectée n'a été supprimée ; aucune collecte de personnes n'a été activée.
