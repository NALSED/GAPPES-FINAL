# CERTIFICATION — score continu, classement et volume (mission D62)

Ce document porte le **verdict** de la mission `DECISION_AUTOCAL.md`. Il est écrit en deux temps : les critères sont
**pré-enregistrés** ci-dessous (avant toute mesure sur le jeu de test) ; le verdict est ajouté à la suite, sans
toucher aux critères. Déplacer un critère après avoir vu les résultats annule la certification.

Verdict : **NON RENDU** (mission en cours). Il sera « certifié » ou « non certifié », jamais entre les deux.

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
* **Ligne B (complémentaire)** : les seuls sujets positifs du test à « liste fermée et quasi complète ». Règle
  **objective, fixée ici avant ouverture** : pour un sujet, si un code d'activité NAF recouvre la phrase (recouvrement
  >= 0,6, `decouverte.traduction.code_naf`), on compte le total T d'établissements actifs que SIRENE/RNA renvoie pour ce
  code (même requête que `docs/conception/calibration.md` § 5) ; le sujet est « à liste fermée » si **R / T >= 0,5**
  (le conseil régional de l'ordre : 72 % ; les chorales : 1,7 %). Sans code NAF fiable, ou sans total lisible : le sujet
  n'est **pas** classé fermé (on ne devine pas). Si aucun sujet ne remplit la règle, la ligne B est « non évaluable »
  et le dit. La règle ne regarde que la phrase, R et le registre, jamais un résultat du système.
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

*(à écrire après l'ouverture unique du jeu test)*
