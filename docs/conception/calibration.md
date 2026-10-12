# Calibration et mesures de l'indice de fiabilité (mission D62, décisions D64 et D65)

Document de travail de la mission d'autocalibration. Il rassemble les mesures **sur les jeux de mise au point (dev) et de validation uniquement** ; le jeu de test est fermé (aucune mesure, aucune lecture de résultat). Toutes les mesures se rejouent depuis les archives (zéro requête réseau, Wikidata jugé depuis son cache disque). Les critères de `docs/CERTIFICATION.md` sont inchangés.

Ce document est en cours de rédaction ; il sera complété par l'étude Optuna, la calibration, le diagramme de fiabilité, les ablations et la mesure de `min_ecosystemes = 1` avant l'ouverture unique du test.

## 0. Réserve de méthode qui commande la lecture de tout le reste (circularité)

Les **références** de tous nos sujets viennent de Wikidata (supervision distante). Wikidata est aussi, depuis D63, un fournisseur de candidats. Un fournisseur Wikidata jugé contre une référence Wikidata se retrouve lui-même : **ce n'est pas une mesure**. Règle appliquée (D64, étape 1) : pendant la mesure, le fournisseur Wikidata est désactivé ; ses chiffres sont donnés « circulaire, information » et ne comptent dans aucune conclusion. Seuls comptent : le web seul, SIRENE/RNA et les noms lus dans les textes. Aucun de nos sujets n'a de référence indépendante des registres : l'apport propre de SIRENE/RNA n'est donc mesurable que par le recoupement SIREN et libellé (peu de références portent un SIREN : 0 à 62 % selon le sujet).

## 1. Validité de la mesure : les scores sont-ils des égalités ? (point 1 de Sednal)

Sur `handball-pro` (R = 17), pour les six configurations de comparaison :

| configuration | candidats | valeurs de score distinctes | plus grand groupe d'ex æquo | valeurs distinctes dans le top 17 | justes dans le top 17 |
|---|---|---|---|---|---|
| web seul | 15 | 15 | 1 | 15 | 1 |
| + SIRENE | 17 | 16 | 2 | 16 | 1 |
| + noms | 188 | 188 | 1 | 17 | 1 |
| + SIRENE + noms | 187 | 187 | 1 | 17 | 1 |
| sans fusion de variantes | 281 | 280 | 2 | 16 | 1 |
| vote majoritaire (mesure du matin) | 17 | 17 | 1 | 17 | 1 |

**Verdict sur handball : la mesure est valide.** Les scores sont presque tous distincts, et le top 17 change profondément d'une configuration à l'autre (9 candidats sur 17 seulement en commun entre « web seul » et « + noms »). La R-précision identique (0,0588 = 1/17) vient d'**un seul juste, stable, au rang 7** (Istres Provence Handball) ; le second juste (US Créteil) reste au rang 78. C'est le plafond de rappel, pas un défaut de l'indicateur.

**Mais la vérification a trouvé un vrai défaut sur d'autres sujets.** Sur les 12 sujets de dev et de validation, 3 ont des égalités massives à la frontière du top R :

| sujet | R | candidats | valeurs distinctes | ex æquo à la frontière |
|---|---|---|---|---|
| chorale (`g-q131186`) | 33 | 376 | 192 | **185** |
| faculté (`g-q180958`) | 100 | 379 | 244 | **136** |
| centre des arts (`g-q2190251`) | 89 | 358 | 212 | **147** |

Ce sont des entités SIRENE/RNA qui ne portent aucun autre élément que leur appartenance au registre : même indice, départage alphabétique arbitraire. **Correction appliquée** : la R-précision est désormais rapportée aussi en **valeur espérée sous ex æquo** (`Rprec_ex_aequo`, valeur exacte hypergéométrique : les places restantes à la frontière se partagent à parts égales entre les ex æquo), qui ne dépend plus de l'ordre alphabétique. Dans les tableaux ci-dessous les deux colonnes sont données ; elles coïncident dès qu'il n'y a pas d'égalité réelle à la frontière. Les 9 autres sujets n'ont pas d'égalité à la frontière (au plus 2 candidats).

## 2. Traduction du sujet en requête de registre (point 2)

Comparaison par sujet entre ce que produit la traduction de la phrase et la requête qui a bâti la référence, **quand le fonds interrogé est le même** (Wikidata). Toutes les références de dev et de validation sont des requêtes SPARQL rejouables ; ce point s'applique donc à tous.

Écart constaté : pour les quatre sujets d'amorçage, la référence vient d'une requête que la phrase ne décrit pas directement (ex. handball : `?item wdt:P118 ?l` sur les ligues professionnelles) ; pour les sujets `g-*`, la référence est la classe du sujet et la traduction la retrouvait déjà. Le défaut de la traduction (v1) était de chercher **une seule classe** pour la tête de la phrase (« club de handball », 12 éléments en France, dont 1 dans la référence), alors que la phrase décrit un **type + un domaine** (« clubs » de « handball ») et que les 17 clubs sont des « équipes de handball » reliées au sport handball par la propriété P641.

**Correction (gabarit unique, valable pour tout sujet, aucun réglage par sujet)** : type + complément. Le complément (« handball », « musique électronique », « CAC 40 ») est cherché dans Wikidata ; les organisations rattachées à ce complément ou à l'un de ses sous-concepts par une propriété d'une liste fixe (sport P641, genre P136, domaine P101, sujet principal P921, partie de P361, membre de P463, secteur P452), dans le pays de la phrase quand elle en donne un, sont gardées si leur classe est une organisation ou une sous-classe du type du sujet. Les mots non résolus (« professionnels ») sont retirés un à un (au plus deux) et **signalés**. Priorité : classe couvrant toute la phrase > gabarit type + domaine > classe partielle.

Avant / après, rappel de la liste de référence et taille de la liste produite :

| sujet | R | avant : retrouvés / produits | après : retrouvés / produits | requête retenue |
|---|---|---|---|---|
| handball-pro | 17 | 1 / 12 | **17 / 209** | domaine handball (Q8418), France |
| festivals-elec | 7 | 7 / 453 | **7 / 40** | domaine musique électronique (Q9778), France |
| cac40 | 40 | 0 / 0 | **40 / 48** | domaine CAC 40 (Q648828) |
| supporters-foot | 4 | 0 / 0 | **4 / 4** | classe « groupe de supporters » (Q1070414) |
| g-q212805 | 45 | 45 / 45 | 45 / 45 | classe (identique à la référence) |
| g-q131186 | 33 | 33 / 33 | 33 / 33 | idem |
| g-q742421 | 142 | 142 / 142 | 142 / 142 | idem |
| g-q180958 | 100 | 100 / 100 | 100 / 100 | idem |
| g-q654502 | 21 | 21 / 21 | 21 / 21 | idem |
| g-q2190251 | 89 | 89 / 89 | 89 / 89 | idem |
| g-q56199177 | 23 | 23 / 23 | 23 / 23 | idem |
| g-q43009164 | 104 | 104 / 104 | 104 / 104 | idem |
| 3 témoins | 0 | 0 / 0 | **0 / 0** | aucune classe ni domaine résolus |

Trois remarques de méthode. (a) Le gabarit a été conçu en regardant les quatre sujets d'amorçage de dev et de validation : il peut être sur-ajusté à eux ; les sujets du jeu test sont tous des classes simples où la traduction v1 suffisait, ce qui ne dit rien de plus. (b) Un défaut annexe est corrigé : le pluriel était cherché sous une forme tronquée (« group de supporter ») ; il est désormais cherché sous la forme du mot entier. (c) Pour handball, 209 éléments sont produits pour 17 attendus : la traduction ne sait pas rendre « professionnels » (une ligue, pas une classe) ; la liste produite contient donc tous les clubs de handball de France, dont les 17. Les départager est le travail des autres éléments d'observation (web, noms dans les textes). Le rappel est complet ; la précision dépend du classement.

**Cette mesure est circulaire par construction** (même fonds, même requête) : elle valide la traduction, pas le système. Le chiffre de villes est un acquis : avec le gabarit, 90 des 209 éléments handball portent une commune de registre (avant : 12 sur 17 pour l'ancienne liste).

## 3. Fausses réponses de la reconnaissance de noms : effet du seuil (point 3)

Mesuré sur dev + validation (12 sujets), candidats « noms lus dans les textes » seuls, jugés par la référence (juste / faux / non vérifiable) :

| seuil de confiance | candidats | justes | faux | non vérifiables | part de faux |
|---|---|---|---|---|---|
| 0,85 (avant) | 5 343 | 79 | 1 875 | 3 389 | 35,1 % |
| 0,90 | 4 730 | 79 | 1 692 | 2 959 | 35,8 % |
| **0,93 (retenu)** | 4 232 | **79** | **1 528** | 2 625 | 36,1 % |
| 0,95 | 3 777 | 77 | 1 419 | 2 281 | 37,6 % |
| 0,97 | 3 146 | 71 | 1 216 | 1 859 | 38,7 % |
| 0,98 | 2 649 | 69 | 1 035 | 1 545 | 39,1 % |
| 0,99 | 1 629 | 60 | 657 | 912 | 40,3 % |

**Retenu : 0,93.** C'est le réglage le plus sévère qui ne perd aucune bonne réponse (79 sur 79) : il retire **347 faux (−18,5 %)** et 1 111 candidats au total. Sur handball : 63 -> 53 faux, 5 justes conservés. **Constat à ne pas surinterpréter** : la *part* de faux ne baisse pas quand le seuil monte (elle monte de 35 à 40 %). Les faux sont des détections que le modèle juge sûres (lieux, universités, médias, autres organisations nommées comme telles dans le texte) ; la confiance du modèle mesure « c'est une organisation », pas « c'est une organisation du sujet ». Couper plus haut perd des bonnes réponses plus vite que des faux. Réduire les faux au-delà demande un signal d'appartenance au sujet (corroboration par plusieurs éditeurs, appartenance à un registre), c'est le rôle de l'indice de vraisemblance, pas du seuil.

Sont comptés « faux » les noms dont le libellé exact est celui d'éléments Wikidata d'une autre classe (une ville, une personne) ; un nom d'organisation réel mais hors sujet est « non vérifiable ». Le « faux » est donc un plancher du taux d'erreur réel.

## 4. Fusion des variantes : vérification, rien corrigé (point 4)

Chiffres de départ (seuil de noms 0,85) : la fusion fait passer handball de 281 candidats et 5 justes (**4 entités distinctes**) à 187 candidats et 2 justes. **Hypothèse de Sednal : les deux justes perdus étaient deux écritures d'une même entité. Réponse : fausse.** Les deux entités perdues sont **deux entités différentes**, et chacune est perdue pour une raison qui n'est pas « la fusion fait son travail » :

* « HBC Nantes » et « Handball Club de Nantes » sont bien deux écritures du même élément (Q939580), comptées deux fois avant la fusion : c'est le doublon légitime (5 justes = 4 entités). Mais après fusion **Nantes n'était plus juste du tout** : « Handball Club de Nantes » avait été absorbé dans un groupe géant de noms sans rapport, et le groupe « HBC Nantes / HBC Nantes SAS » avait un représentant que la référence ne reconnaît pas.
* « USAM Nîmes Gard » (Q595394) : le groupe « USAM / USAM Nimes Gard / USAM Nîmes Gard Nîmoises / … » est correctement réuni, mais le représentant retenu (le plus documenté) a une écriture que la référence ne reconnaît pas ; l'entité est perdue **au jugement**, pas à la découverte.

Avec le seuil de noms retenu depuis (0,93, D65), la même vérification donne 217 candidats et 5 justes (4 entités) sans fusion, **151 candidats et 3 justes (3 entités)** avec fusion : Nantes est conservé (le représentant est « HBC Nantes »), USAM Nîmes Gard est toujours perdu. Une entité sur quatre est donc perdue à tort, une (le doublon Nantes) est réunie à raison.

**Défaut de fond constaté** : le regroupement de nomenklatura est transitif. Un mot générique (« club », « handball ») relie des noms qui n'ont rien à voir : le plus grand groupe compte 37 noms au seuil 0,93 (de l'ordre de 45 à 0,85) et mêle « Club », « Club of France », « Georgetown University », « England Handball Association », « Metz Handball »… Le score `name-based` donne aussi 0,91 entre « Conseil régional de l'ordre des experts-comptables de Lyon » et « … de Paris », deux entités distinctes.

Rien n'est corrigé ici, comme demandé. Pistes à décider ensuite : grouper sans chaînage (lien complet) ; interdire les mots génériques comme pont ; juger une ligne sur **toutes** les écritures de son groupe plutôt que sur celle du représentant ; garde-fou par commune (déjà en place).

## 5. Le critère de 0,90 : sur quels sujets est-il atteignable ? (point 5, constat sans décision)

Mesure : taille R de la liste de contrôle comparée au nombre total d'entités actives que SIRENE/RNA renvoie pour la même requête (borne basse de la population réelle), et part des entités de référence qui portent un site officiel (P856) ou un SIREN (P1616), c'est-à-dire que le système peut confirmer.

| sujet | R | total SIRENE/RNA (même requête) | R / total | site P856 | SIREN P1616 | nature de la liste |
|---|---|---|---|---|---|---|
| cac40 | 40 | (non applicable : liste de 40 par définition) | 100 % | 100 % | 93 % | **fermée, complète** |
| g-q56199177 (conseil régional de l'ordre) | 23 | 32 | 72 % | 100 % | 0 % | **fermée, quasi complète** |
| handball-pro | 17 | n.d. (liste d'une division) | — | 100 % | 6 % | fermée en droit (une division), mais la phrase ne le dit pas |
| supporters-foot | 4 | n.d. | — | 25 % | 25 % | très partielle (quatre groupes) |
| festivals-elec | 7 | n.d. | — | 100 % | 0 % | partielle (7 festivals) |
| g-q43009164 (rugby à XV) | 104 | n.d. | — | 65 % | 4 % | assez complète pour un sport, mais incomplète |
| g-q742421 (troupes théâtrales) | 142 | 73 (nom seul, non fiable) | — | 26 % | 7 % | partielle |
| g-q2190251 (centres des arts) | 89 | 487 | 18 % | 79 % | 2 % | partielle |
| g-q212805 (bibliothèques numériques) | 45 | n.d. | — | 98 % | 0 % | partielle |
| g-q131186 (chorales) | 33 | 1 954 | 1,7 % | 64 % | 12 % | **très partielle** |
| g-q180958 (facultés) | 100 | 1 727 | 5,8 % | 60 % | 0 % | **partielle** |
| g-q654502 (SAS) | 21 | 863 | 2,4 % | 90 % | 62 % | **très partielle** (des centaines de milliers de SAS réelles) |

(n.d. : la requête par nom de la phrase entière ne renvoie pas un total interprétable. Les totaux SIRENE sont des **bornes basses grossières**, pas des effectifs.)

**Constat.** Le critère « R-précision stricte ≥ 0,90 » ne garde son sens que sur les **listes fermées et quasi complètes** : parmi dev et validation, `cac40` et le conseil régional de l'ordre, éventuellement handball (une division). Sur tout sujet à liste partielle (chorales, SAS, facultés, centres des arts, troupes…), la référence ne contient que 2 à 18 % de la population visible : un système qui trouve des acteurs réels hors de la liste est **puni** (ils comptent « non vérifiables », non pertinents au sens strict) et un système parfait ne peut pas atteindre 0,90 **par construction**. La moyenne de six sujets du test, avec cette composition, ne peut donc dépasser 0,90 que si la plupart des six sont des listes fermées. Le classement des six sujets du test selon cette grille n'a **pas** été fait (le test est fermé) ; il le sera à partir de leur seule définition, avant ouverture, si Sednal le décide.

**Options à trancher par Sednal** (rien n'est modifié) :

1. garder le critère 0,90 sur la moyenne des six sujets du test tel quel (verdict probablement « non certifié » quelles que soient les qualités du système) ;
2. ajouter, **avant ouverture du test**, une seconde ligne de verdict calculée sur les seuls sujets à liste fermée et quasi complète, présentée à côté de la première sans la remplacer ;
3. remplacer la mesure stricte par une mesure qui crédite aussi les « non vérifiables » plausibles (précision estimée par échantillon vérifié à la main), au prix de perdre le caractère automatique ;
4. construire pour quelques sujets une référence indépendante d'un seul registre (par exemple un annuaire officiel) pour pouvoir mesurer SIRENE/RNA sans circularité.

## 6. Collecte non élargie (point 6)

Aucune collecte supplémentaire n'a été lancée. Les trois cycles réels supplémentaires sur deux sujets (mesurés plus haut dans la mission) n'avaient pas déplacé le plafond de rappel ; avec la traduction corrigée, le plafond du **fournisseur de registre** est désormais de 100 % de la liste quand le fonds est le même (§ 2), ce qui change la donne : une collecte plus grande ne sera rechiffrée qu'une fois les étapes suivantes mesurées, sur la base de la traduction corrigée.

## 7. Mesure d'ensemble sur dev et validation (R-précision stricte)

Chiffre de départ du matin (autocal/resultats/base_dev.json et base_validation.json) : **0,020** en dev et **0,007** en validation, identique pour le système actuel, le vote majoritaire et les cinq algorithmes de découverte de vérité.

| configuration (indice de vraisemblance, valeurs d'expert non réglées) | dev | validation | dev, sous ex æquo | validation, sous ex æquo | bpref (dev + val) |
|---|---|---|---|---|---|
| web seul | 0,018 | 0,007 | 0,018 | 0,007 | 0,006 |
| + SIRENE/RNA | 0,018 | 0,022 | 0,018 | 0,022 | 0,009 |
| + noms lus dans les textes (seuil 0,93) | 0,018 | 0,068 | 0,018 | 0,068 | 0,051 |
| **+ SIRENE/RNA + noms (non circulaire)** | **0,018** | **0,068** | 0,018 | 0,068 | 0,051 |
| + Wikidata seul (circulaire, information) | 0,578 | 0,919 | 0,573 | 0,920 | 0,789 |
| tout (circulaire, information) | 0,502 | 0,726 | 0,484 | 0,726 | 0,652 |

Lecture honnête. Sans Wikidata, le gain mesurable sur la validation est de 0,007 à 0,068 (surtout le CAC 40 : 0,35 grâce aux noms lus, et le rugby : 0,058) ; sur dev il n'y a **aucun gain** (0,020 -> 0,018). Les chiffres avec Wikidata (0,58 et 0,92) ne prouvent rien : le fournisseur retrouve sa propre liste. Les valeurs de l'indice sont celles d'expert de `config/lr.yaml`, pas encore réglées (Optuna) ni calibrées.

## 8. Réglage Optuna et calibration (étape 3, système sans Wikidata)

**Réglage (dev, 108 essais, TPE, graine 62, arrêt par patience ; base `donnees/autocal/optuna.db`, étude `etape3-dev-v1`)**. Objectif : R-précision stricte espérée sous ex æquo (+ 0,01 × précision moyenne pour départager). Bornes fixées avant les résultats (`etape3.BORNES`).

| | dev | validation | écart d'optimisme (dev − val) |
|---|---|---|---|
| valeurs d'expert (`config/lr.yaml`) | 0,0175 | 0,0679 | −0,050 |
| valeurs réglées par Optuna | 0,0209 | 0,0768 | −0,056 |

Le gain du réglage est **négligeable** (+0,003 en dev, +0,009 en validation) et l'écart d'optimisme est négatif (la validation contient le CAC 40, où les noms lus font 0,35). Ce que dit le réglage : fusion de variantes **désactivée** (cohérent avec le § 4), poids SIRENE/RNA presque annulés (0,19 et 0,11), poids des noms lus dans les textes forts (1,9 par éditeur), proximité du texte propre et citations relevées. Le réglage ne peut pas faire mieux parce que **les bons acteurs ne sont pas dans la liste des candidats** (§ 1, § 5), pas parce que l'indice les classe mal.

**Calibration** (ajustée sur dev, vérifiée sur validation, étiquette stricte ; le test n'est pas touché). Peu de positifs : 13 sur 2 060 candidats en dev (0,6 %), 74 sur 3 155 en validation (2,3 %).

| méthode | ECE dev | Brier dev | ECE validation | Brier validation | Brier du prédicteur constant (validation) | p max (validation) | candidats à p ≥ 0,9 |
|---|---|---|---|---|---|---|---|
| Platt | 0,0015 | 0,0061 | 0,0189 | 0,0234 | 0,0229 | 0,79 | 0 |
| isotone | 0,0 | 0,0056 | 0,0186 | 0,0232 | 0,0229 | 0,40 | 0 |

Diagramme de fiabilité : `docs/conception/fiabilite_validation.png`.

Lecture honnête : l'ECE est bas **parce que presque tout est proche du taux de base** (1 à 2 %), pas parce que l'indice est bien calibré ; et le score de Brier **n'est pas meilleur que celui du prédicteur constant** en validation (0,0234 contre 0,0229). Sur le système sans Wikidata, l'indice n'a donc pas de pouvoir discriminant mesurable contre cette référence, ce qui ferait échouer le critère 5 de la certification (Brier < constant). Aucun candidat n'atteint 0,9 : aucun résultat ne serait présenté en confiance haute. La calibration d'un système AVEC Wikidata serait circulaire (beaucoup de positifs, mais ce sont les siens) et n'est pas présentée comme une mesure ; hors du domaine calibré (sujets informels, personnes), le chiffre est une estimation étendue, dit sur la ligne de sortie (colonne `calibre`).

## 9. Ablations et mesure de `min_ecosystemes = 1`

**Ablations** (système sans Wikidata, paramètres réglés ; R-précision stricte espérée sous ex æquo, moyenne par jeu ; `autocal/resultats/etape3_ablation.json`) :

| configuration | dev | validation | bpref dev | bpref validation |
|---|---|---|---|---|
| complet (réglé, sans Wikidata) | 0,0209 | 0,0768 | 0,0205 | 0,1036 |
| sans SIRENE/RNA | 0,0209 | 0,0768 | 0,0205 | 0,1036 |
| **sans noms lus** | 0,0197 | **0,0205** | 0,0109 | 0,0085 |
| sans proximité du texte propre | 0,0073 | 0,0851 | 0,0095 | 0,1074 |
| sans écosystèmes | 0,0209 | 0,0768 | 0,0205 | 0,1036 |
| sans citations | 0,0209 | 0,0768 | 0,0203 | 0,1032 |
| web seul (aucun fournisseur) | 0,0197 | 0,0072 | 0,0106 | 0,0060 |
| système d'avant la mission (« actuel ») | 0,0197 | 0,0072 | 0,0080 | 0,0060 |
| vote majoritaire | 0,0197 | 0,0072 | 0,0068 | 0,0072 |

Les **noms lus dans les textes sont le seul élément qui apporte quelque chose** de mesurable (validation 0,0205 -> 0,0768 ; presque tout vient du CAC 40). SIRENE/RNA, les écosystèmes et les citations n'apportent rien contre cette référence (ce qui ne prouve pas qu'ils n'apportent rien : leurs apports ne sont pas vérifiables ici). La proximité du texte propre fait mieux en dev et moins bien en validation : réglage instable. Le système d'avant la mission et le vote majoritaire sont identiques (0,0197 / 0,0072).

**`min_ecosystemes` à 1 (mesure, jamais appliquée).** Le minimum d'écosystèmes du recoupement (`crossref.min_ecosystems`) et celui de l'apprentissage (`autonomie.min_ecosystemes`) passés à 1 sur les 12 sujets, rejeu complet (`autocal/resultats/etape3_min1.json`) :

| | candidats web (dev / val) | R-précision « actuel » (dev / val) | R-précision indice réglé (dev / val) |
|---|---|---|---|
| valeur 2 (défaut) | 181 / 186 | 0,0197 / 0,0072 | 0,0209 / 0,0768 |
| valeur 1 (mesure) | **245 / 254** | 0,0197 / 0,0072 | 0,0209 / 0,0768 |

La valeur 1 ajoute **+35 % de candidats** web (+64 en dev, +68 en validation) **sans aucune bonne réponse de plus** : R-précision strictement identique. Rapporté, non appliqué, comme demandé : le défaut reste deux.

## 10. Intégration en production (inactive par défaut)

* `grappes.classement.production` : candidats du web + registres + noms lus -> indice de vraisemblance -> probabilité -> lignes de sortie. Branché dans le cycle (`cycle/engine.py`) et dans `grappes export` par `config/classement.yaml` ; **`actif: false` par défaut** : tant que Sednal ne l'active pas, le cycle ne change pas.
* Activé, il écrit les profils de `config/sortie.yaml` (notamment `resultat_brut.csv` : nom, ville, pays, score, bande verbale, `calibre`, registres, sources). `resultat.csv` et `resultat_tsites.csv` ne changent que si `remplace_resultat: true`.
* Essai de bout en bout sur handball (rejeu, sans réseau) : 211 lignes, communes remplies (Metz, Dijon, Istres, Plan-de-Cuques…), colonne `calibre` = « estimation étendue ». Une erreur du classement n'interrompt jamais le cycle (écrite dans `sorties/classement_erreur.txt`).
* `config/calibration.json` : **calibration non valide** (méthode « aucune », `valide: false`) ; le score affiché est `p = LR/(1+LR)` (rapport de cotes a priori 1:1), plafonné à 99, toujours étiqueté estimation étendue. Il passera à « mesuré » seulement quand une calibration battra le prédicteur constant en validation.
* Les réponses des registres sont mises en cache sur disque avec une durée de vie de 30 jours.

## 11. Ouverture du jeu test et verdict (2026-10-12)

Option 2 retenue par Sednal (D66), règle de la ligne B fixée avant ouverture, test ouvert une fois (D67). Résultat :
**non certifié** sur les deux lignes ; R-précision stricte moyenne **0,0178** (cible 0,90), Brier 0,00680 contre 0,00651
pour le prédicteur constant, 1 sujet sur 6 au-dessus du 95e centile de permutation. Cause mesurée : **11 acteurs de la
référence sur 356 (3,1 %)** sont parmi les candidats, tous classements confondus ; le classement ne peut donc pas
corriger ce que les sources ne fournissent pas. Le gain des noms lus observé en validation (0,007 → 0,077) tenait
presque entièrement à cac40 et ne se retrouve pas sur le test (0,0160 → 0,0178). Détail, tableaux, hypothèses
contredites : `docs/CERTIFICATION.md` § 2. Diagramme : `docs/conception/fiabilite_test.png`.

## 12. Reste à faire (propositions à Sednal, rien de décidé)

1. Wikidata comme fournisseur de **découverte** en production (« estimation étendue », car circulaire) : seul levier qui
   a montré un rappel élevé (0,58 / 0,92 sur dev / validation, non probant).
2. Référence indépendante d'un registre pour quelques sujets (option 4 du § 5) afin de mesurer SIRENE/RNA.
3. Mesurer un élargissement de la collecte web (point 6) sur dev d'abord ; un nouveau jeu test (nouvelle graine) sera
   nécessaire pour toute certification ultérieure.
4. Activation éventuelle de `config/classement.yaml: actif`, sort de la fusion de variantes (§ 4), poids de Wikidata dans l'indice.
