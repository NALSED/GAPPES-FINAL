# Cibles, vérificateur de type et amorces (D69)

Décision de Sednal : `DECISION_CIBLE.md` (numérotée « D69 » par Sednal, numéro libre suivant). Mesures sur la mise au
point et la validation uniquement : le jeu test est brûlé (D67) et n'a servi à rien ici.

## 1. L'état de l'art mondial, vérifié à la source

La tâche (« entity list completion » / « related entity finding ») a été évaluée par le NIST (TREC Entity Track 2010 et
2011), puis sur DBpedia-Entity v2. J'ai relu les vues d'ensemble officielles (PDF du NIST) :

| Mesure annoncée par Sednal | Ce que j'ai lu | Verdict |
|---|---|---|
| R-précision 0,31 (TREC 2010) | Vue d'ensemble 2010, tableau 1 (REF, meilleur run automatique `bitDSHPRun`, BIT) : **rPrec 0,3075** ; tableau 4 (ELC, `KMR5PU`, Purdue) : **rPrec 0,3116**, MAP 0,2613 | confirmé (0,31) |
| R-précision 0,29 (TREC 2011, suspendu en 2012) | Vue d'ensemble 2011, tableau 3 (REF, `PRISREF1`, manuel) : **R-Prec 0,2908** ; texte : « we decided to put the track on hold for 2012 » | confirmé (0,29) |
| nDCG@10 0,54 (2022) | EM-BERT (arXiv 2205.00820), tableau 2, DBpedia-Entity v2, total : **nDCG@10 0,541** (sous-ensemble ListSearch : 0,544) | confirmé (0,54) |
| nDCG@10 0,44 (2017) | non retrouvé à la source dans cette session | non vérifié |
| nDCG@10 0,52 (2025) | non retrouvé (les recherches ne rendent que des reprises de travaux de 2020 : BM25F-CA + Wikipedia2Vec 0,484, GEEER 0,487) | non vérifié |

Réserves que le document doit porter :

* **Les deux mesures ne sont pas comparables.** R-précision (TREC) = précision au rang R sur une liste de réponses
  d'entités ; nDCG@10 (DBpedia-Entity) = qualité des dix premiers résultats, jugements gradués. Le critère 0,90 de
  grappes est une R-précision : seuls 0,31 et 0,29 lui sont comparables.
* **TREC 2010 ELC est très petit** : 3 groupes, 5 runs. La R-précision 0,3116 de Purdue vient d'un seul run sur un
  petit jeu de sujets ; à lire comme un ordre de grandeur, pas comme un record statistiquement solide. Les résultats ELC
  de 2011 n'étaient pas publiés dans la vue d'ensemble (« not yet available at the time of writing »).
* **Les sujets TREC ne sont pas les nôtres** : requêtes en anglais sur ClueWeb09/BTC, exemples fournis en entrée
  (2 à 23), types limités à quatre (personne, organisation, lieu, produit). grappes part d'une phrase seule, en
  français, sur des acteurs français.

Conclusion de Sednal confirmée par la lecture : le critère de 0,90, appliqué à tous les sujets, est hors de portée de
tout système publié. Il n'a de sens que là où une liste faisant autorité existe.

## 2. Deux cibles (point 1)

Règle fixée **avant toute mesure** et sur la seule phrase (`autocal/cibles.json`, commit `c1c9340`) :

* **Cible A, registre officiel (R-précision >= 0,90)** : chaque membre de la catégorie doit, pour exister en droit,
  être inscrit à un registre public français (RCS/SIRENE pour une société, RNA pour une association) ou tenir son statut
  d'une autorité publique (ordre professionnel, label, classement officiel) ; ou la phrase restreint la catégorie à un
  statut encadré (« professionnels », « du CAC 40 »).
* **Cible B, pas de liste faisant autorité (R-précision de 0,30 à 0,40 = niveau de l'état de l'art mondial)** : une
  partie notable de la catégorie existe sans inscription (acteurs informels), ou les membres n'ont pas de personnalité
  juridique propre (événements, services, composantes, lieux), ou la catégorie est ouverte.
* Les témoins (R = 0) n'ont pas de cible.

| Jeu | Cible A | Cible B |
|---|---|---|
| Mise au point | handball-pro | festivals-elec, bibliothèque numérique, chorale, troupe théâtrale, faculté |
| Validation | cac40, société par actions simplifiée, conseil régional de l'ordre des experts-comptables | centre des arts, supporters-foot, club de rugby à XV |
| Test (consigné, non mesuré) | pôle de compétitivité, conservatoire à rayonnement régional, brasserie | bibliothèque universitaire, groupe de pression, ensemble musical |

Deux limites à lire : la cible B est un niveau **de recherche publiée**, pas une garantie pour grappes ; et la règle est
plus large que la « ligne B » de la certification (D66, listes fermées par autorité publique), qui reste inchangée.

### Où en est grappes, cible par cible (R-précision stricte moyenne ; `autocal/resultats/cibles_*.json`)

| Jeu | Cible | Sujets | Système figé (D67) | + prises (D68) | + prises + type (D69) | Cible |
|---|---|---|---|---|---|---|
| Mise au point | A (registre officiel) | 1 | 0,059 | 0,059 | 0,059 | >= 0,90 |
| Mise au point | B (sans liste) | 5 | 0,013 | 0,012 | 0,013 | 0,30 à 0,40 |
| Validation | A | 3 | 0,131 | 0,131 | 0,131 | >= 0,90 |
| Validation | B | 3 | 0,022 | 0,026 | 0,026 | 0,30 à 0,40 |

Rendus séparés, jamais fusionnés. Lecture : l'écart à la cible est de 7 à 15 fois en A et de 12 à 23 fois en B.
La cible A est elle-même tirée vers le bas par la qualité de la référence (Wikidata, incomplète) et par le fait qu'un nom
du registre n'est pas un nom de Wikidata ; sur « Les entreprises du CAC 40 », 37 des 40 acteurs sont déjà parmi les
candidats mais la R-précision n'est que de 0,35 : ici c'est le **classement** qui plafonne, pas la découverte.
Le jeu test n'est pas mesuré (brûlé).

## 3. Vérificateur de type (point 2)

Idée de Purdue (TREC 2010) : avant de classer un candidat, vérifier que son type correspond au type demandé.
Implémentation : `src/grappes/decouverte/verification_type.py`, appelée par `decouvrir()` sur les candidats des prises
YAML, **en amont du classement** (`DecouverteConfig.verifier_type`, vrai par défaut ; le classement reste inactif).

* **Type demandé**, de la seule phrase : la racine du premier mot plein (« clubs », « festivals », « chorale »), sans le
  complément de domaine (« handball »), car un nom qui contient « handball » ne prouve pas que ce soit un club.
* **Type du candidat** : ce que sa source déclare. Prise `culture_festivals` : `type_fixe: festival` ; prise
  `culture_spectacles` : code NAF de la ligne (remplacé par son libellé officiel) et nature juridique ; prise
  `esr_etablissements` : `type_fixe: établissement d'enseignement supérieur` ; prise `bnf_organisations` : rien (la BnF ne
  dit que `foaf:Organization`).
* **Verdict à trois valeurs** : *compatible* (le type déclaré porte un mot du type demandé), *incompatible* (nature
  « personne physique », ou type déclaré sans aucun mot du type demandé), *inconnu* (la source ne déclare rien : GARDÉ).
  On n'écarte que sur une preuve ; on ne devine jamais le type d'après le nom.
* **Le nom n'est pas une preuve de type.** Première version, écartée avant toute application : un candidat dont le
  nom portait le mot du type était jugé compatible. Or la requête, relaxée au type seul, cherche précisément ce mot dans
  le nom : la preuve était circulaire (429 des 542 lignes de licences trouvées pour « clubs de handball » étaient des
  « comedy club », « hot club de jazz »…). La règle a été retirée.
* Aucun code propre à un sujet : la règle est la même pour tous ; les types déclarés sont des faits sur les sources,
  écrits une fois dans leur YAML.

## 4. Effet mesuré du vérificateur de type (`autocal/resultats/type_dev.json`, `type_validation.json`)

Candidats ajoutés par les prises YAML (les « 2 063 en trop » de D68), avant et après le vérificateur :

| Jeu | Avant | Après | Retirés (jugés faux / non vérifiables / **justes**) | Acteurs de la référence perdus |
|---|---|---|---|---|
| Mise au point | 2 063 | 1 242 (−40 %) | 91 / 731 / **0** | 0 |
| Validation | 3 167 | 395 (−88 %) | 302 / 2 471 / **0** | 0 |

* **Les 242 entrepreneurs de spectacles arrivés sur le handball** : 242 → **4**. Les retirés sont des débits de boisson,
  restaurants, hôtels, campings, personnes physiques, « arts du spectacle
  vivant » sans mot « club », etc.
* **Le festival-bruit** : les 389 festivals arrivés sur « bibliothèque numérique » et 14, 19 et 3 sur la troupe, le handball et
  la chorale sont retirés (type « festival » contre type demandé).
* R-précision : inchangée partout sauf la troupe théâtrale (0,007 → 0,014 : moins d'ex æquo parasites).
* **Ce qu'il ne retire pas** : (1) les ~700 candidats de la BnF (la BnF ne déclare aucun type, donc « inconnu », gardé) ;
  (2) les 532 festivals de « musique électronique » : leur type est le bon (« festival »), c'est leur **domaine** qui est
  faux, parce que la requête a été relaxée à « musique » seul. C'est un défaut de la relaxation, pas du type : le
  vérificateur ne peut pas le corriger sans règle inventée ; (3) sur la validation, les 300 « centres » de la BnF.
* **Risque non mesurable par la référence** : la comparaison est lexicale. Les 227 licences « arts du spectacle vivant »
  retirées pour la troupe théâtrale sont peut-être de vraies troupes (« compagnie » n'est pas « troupe ») ; la
  référence, tirée de Wikidata, n'en reconnaît aucune, donc la perte éventuelle est invisible. Aucune liste de synonymes
  n'est inventée : c'est une décision de Sednal (un thésaurus de types, ou le rattachement NAF ↔ classe).
* **Réserve de méthode** : la première version acceptait « le nom porte le type demandé » ; elle a été écartée avant
  application parce que circulaire (voir § 3). L'effet de la première version (242 → 177) n'est pas retenu.

## 5. Les amorces : 3 exemples fournis en entrée (`autocal/resultats/amorces_dev.json`, `amorces_validation.json`)

Rien n'est activé. 3 acteurs de la référence tirés au sort (graine 20261012, 5 tirages par sujet), retirés de la
référence et du classement avant de mesurer (on compte des entités nouvelles, comme TREC). Mécanisme mesuré : le code
NAF des exemples dans SIRENE remplace le code NAF que la phrase ne trouve presque jamais (`code_naf` rend « aucun » sur
les 12 sujets) ; la découverte SIRENE par code NAF + mots du complément s'applique ensuite. Wikidata n'est pas utilisé
(la référence en dérive : le gain serait fictif).

| Jeu | Tirages | Tirages où un code NAF est retenu | Acteurs de référence gagnés | Candidats ajoutés (moyenne) | R-précision mieux / pire |
|---|---|---|---|---|---|
| Mise au point | 30 | 21 | **0** | 37 | 0 / 4 |
| Validation | 30 | 24 | **0** | 12 | 0 / 0 |

* **Le gain est nul sur 60 tirages.** Le coût n'est pas nul : jusqu'à 311 candidats ajoutés (chorale), et la
  R-précision de la troupe baisse dans 4 tirages.
* Un exemple est déjà parmi les candidats en moyenne dans 0,33 cas sur 3 (mise au point) et 0,67 sur 3 (validation) :
  trop peu pour que la co-citation dans les textes déjà collectés serve.
* **Ce que cette mesure ne dit pas** : l'apport des exemples dans TREC vient surtout de leur usage comme **requêtes
  de recherche** (trouver les pages qui les citent, puis les autres noms de ces pages). Cela demande une nouvelle
  collecte (crédits Tavily) et n'a pas été fait : « sans rien activer » interdit de collecter. L'estimation de coût :
  une requête par exemple et par sujet, soit 3 crédits par sujet. Le gain de ce mécanisme-là est **inconnu**, pas nul.
* **Conclusion pour Sednal** : le gain n'est pas net avec ce que le système sait faire aujourd'hui. L'entrée « 3 exemples »
  ne se justifierait que si elle déclenche une collecte web à partir de leurs noms ; à mesurer avant de décider.

## 6. Les prises data.gouv.fr sur la validation (`autocal/resultats/sources_validation.json`)

La question de Sednal : le gain de +2 points vu sur la mise au point est-il réel ou un ajustement à six sujets ?

| Jeu | Acteurs de référence parmi les candidats, avec les prises | Candidats ajoutés |
|---|---|---|
| Mise au point | +8 sur 344 (3,2 % → 5,5 %, soit +2,3 points) | 2 063 |
| Validation | **+1 sur 281** (+0,4 point) | 3 167 |

* **Le gain ne se généralise pas.** Sur la validation, une seule prise rapporte un acteur (BnF : un club de rugby à XV
  sur 104) ; les licences, festivals et établissements ESR n'en rapportent aucun. La R-précision passe de 0,067 à 0,077
  sur le rugby et reste identique ailleurs.
* La mise au point a été regardée pour choisir les prises (handball, festivals, troupe, chorale) : le +2 points est donc
  très probablement de l'ajustement, comme Sednal le soupçonnait. L'écart 2,3 contre 0,4 point ne permet pas, avec six
  sujets, d'affirmer plus.
* Coût de la mesure : environ 2 h (jugement Wikidata). Le sujet « centre des arts » a ajouté à lui seul 2 765 candidats
  (1 391 licences, 1 071 festivals) avant le vérificateur de type, 300 après.

## 7. Propositions (rien n'est appliqué)

1. **Cibles** : adopter A/B pour tout futur jeu test (classification figée avant mesure, comme ici).
2. **Vérificateur** : le garder actif sur les prises (effet net positif, aucune perte mesurée) ; décider d'un thésaurus
   de types si Sednal veut limiter le risque lexical (§ 4).
3. **Prises data.gouv.fr** : le gain est faible hors des sujets pour lesquels elles ont été choisies ; ne pas les compter
   comme un levier général.
4. **Amorces** : mesurer le mécanisme « requêtes web à partir des exemples » avant toute décision (3 crédits Tavily par
   sujet).
5. **Plafond du classement** : sur le CAC 40, 37 acteurs sur 40 sont candidats et la R-précision n'est que de 0,35 ; le
   classement est le goulot pour la cible A, la découverte pour la cible B.
