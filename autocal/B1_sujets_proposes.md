# B1 — Sujets proposés pour la référence indépendante de Wikidata (15/11/2026)

**État : proposition, à valider par Sednal. Aucune liste relevée, aucune collecte lancée.**

But : mesurer le programme contre des listes complètes publiées par une autorité, et non plus contre Wikidata. Deux chiffres suivis ensuite après chaque changement : la part des acteurs attendus que le programme trouve (3 % en octobre), et la part de faux dans ce qu'il sort.

## Coût

* Relevé des listes (téléchargement ou copie depuis le site officiel) : **0 crédit**.
* Collecte : **8 crédits Tavily au plus par sujet** (plafond `requetes_par_cycle` d'`autocal/collecte.py`). Pour 25 sujets : **200 crédits au plus**, une seule fois (les réponses sont enregistrées, les mesures suivantes se rejouent sans réseau ni crédit).
* La collecte demande la clé Tavily : elle se lance sur la machine qui la détient, sur ordre explicite (`collecter --jeu officiel`). La commande `collecter` sans option ne touche jamais à ces sujets.

## Sujets proposés (25)

Les effectifs sont des ordres de grandeur, **à confirmer au relevé** de chaque liste. Un sujet dont la liste ne se retrouve pas sur le site de l'autorité est retiré, pas remplacé par une autre source.

| N° | Phrase du sujet | Autorité qui publie la liste | Effectif approché |
| :-- | :-- | :-- | :-- |
| 1 | scènes nationales | ministère de la Culture (label) | 75 |
| 2 | centres dramatiques nationaux | ministère de la Culture (label) | 38 |
| 3 | centres chorégraphiques nationaux | ministère de la Culture (label) | 19 |
| 4 | fonds régionaux d'art contemporain | ministère de la Culture (label) | 22 |
| 5 | scènes de musiques actuelles | ministère de la Culture (label SMAC) | 90 |
| 6 | centres d'art contemporain d'intérêt national | ministère de la Culture (label) | 50 |
| 7 | conservatoires à rayonnement régional | ministère de la Culture (classement) | 45 |
| 8 | écoles nationales supérieures d'architecture | ministère de la Culture | 20 |
| 9 | maisons des Illustres en Auvergne-Rhône-Alpes | ministère de la Culture (label) | 30 |
| 10 | musées de France en Isère | ministère de la Culture (appellation, données ouvertes) | 40 |
| 11 | parcs naturels régionaux | État (classement par décret), fédération des parcs | 58 |
| 12 | grands sites de France | ministère chargé de l'Environnement (label) | 20 |
| 13 | associations agréées de surveillance de la qualité de l'air | État (agrément) | 18 |
| 14 | éco-organismes agréés | État (agrément) | 25 |
| 15 | pôles de compétitivité | État (label) | 55 |
| 16 | instituts Carnot | ministère chargé de la Recherche (label) | 39 |
| 17 | sociétés d'accélération du transfert de technologies | État | 13 |
| 18 | universités françaises | ministère de l'Enseignement supérieur (liste) | 70 |
| 19 | instituts universitaires de technologie | ministère de l'Enseignement supérieur | 108 |
| 20 | centres hospitaliers universitaires | ministère chargé de la Santé | 32 |
| 21 | fédérations sportives agréées | ministère des Sports (liste des agréments) | 110 |
| 22 | clubs professionnels de football de première et deuxième division | ligue professionnelle (annuaire) | 36 |
| 23 | clubs professionnels de rugby de première et deuxième division | ligue nationale (annuaire) | 30 |
| 24 | banques alimentaires | fédération (annuaire du réseau) | 79 |
| 25 | conseils d'architecture, d'urbanisme et de l'environnement | fédération nationale (annuaire) | 92 |

Répartition voulue : des listes courtes (13) et longues (110), des labels d'État et des annuaires de fédération, des acteurs très présents sur le web (clubs, universités) et peu présents (agréments techniques). Aucun de ces sujets ne touche à des personnes.

## Ce qui est déjà en place (sans coût)

* `python -m grappes.autocal.cli reference-officielle …` transforme une liste relevée en référence au format existant (`autocal/references/`, qrels). Voir `autocal/listes_officielles/LISEZMOI.md`.
* Avec une telle référence, le juge ne consulte jamais Wikidata.

## À décider par Sednal

1. La liste : garder, retirer ou ajouter des sujets.
2. Le budget : 200 crédits Tavily au plus.
3. Voir `QUESTIONS.md` Q-B1 : un nom absent d'une liste officielle complète compte-t-il comme « faux » ?
