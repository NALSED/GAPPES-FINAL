# ECONOMIES — bilan des économies de jetons

Généré le 2026-10-11 11:18 par `outils/bilan_jetons.py` (régénérable : `.venv/bin/python outils/bilan_jetons.py`). Aucune valeur n'est inventée : une donnée absente est écrite « non disponible ».

## 1. Appels routés vers le compte gratuit

* Appels enregistrés : **17**
* Période couverte : du 2026-10-06 au 2026-10-06 (1 jour(s), dont 1 avec au moins un appel)
* Volume estimé en jetons : **non disponible** (le journal ne consigne que l'horodatage et la description : ni jetons, ni octets ; aucune estimation n'est faite à la place)

## 2. Gain du hook RTK (ESTIMATION, pas une mesure)

`rtk gain` donne un gain **estimé** (octets / 4), uniquement sur la sortie que rtk a interceptée (commandes shell et lectures de fichiers). Ce n'est **pas** l'économie totale de jetons ni de coût de la session : il ne couvre ni les réponses du modèle, ni les outils non interceptés, ni le routage vers le compte gratuit.

* Ce projet (`rtk gain --project`) : 143 commandes, 42 690 jetons estimés en entrée, **5 463 jetons estimés économisés** (12.8 % de l'entrée interceptée)
* Compte entier, tous projets : 732 commandes, 534 679 jetons estimés en entrée, **378 392 jetons estimés économisés** (70.8 % de l'entrée interceptée)

## 3. Total consolidé

* **Total consolidé : 5 463 jetons estimés économisés** (gain RTK du projet) + appels gratuits non chiffrables en jetons (voir § 1).
* Marge d'incertitude, **sous hypothèse** de 3 à 5 octets par jeton (RTK suppose 4) : de 4 370 à 7 284 jetons. Ces deux ratios sont des hypothèses modifiables, pas des mesures.
* Le compte gratuit n'ajoute aucun montant : le nombre d'appels est connu, pas leur taille. La somme est donc un **minimum chiffrable**, pas un total.

## 4. Une ligne par jour

| Jour | Appels gratuits | Commandes RTK (projet) | Jetons économisés RTK (projet, estimés) | Gain RTK |
| --- | --- | --- | --- | --- |
| 2026-10-06 | 17 | 124 | 4 613 | 12.0 % |
| 2026-10-11 | non disponible | 19 | 798 | 18.3 % |

## 5. Hypothèses de calcul

* **Journal** : une ligne = un appel routé ; une ligne illisible n'est pas comptée. Dans la période [première ligne, dernière ligne], un jour sans ligne vaut 0 appel ; hors de cette période, la donnée est absente. Le jour est celui de l'horodatage écrit dans la ligne (son propre fuseau).
* **RTK** : les jetons sont ceux que rtk estime (octets / 4). Le périmètre « projet » est celui du dossier courant au lancement ; le périmètre « compte » couvre tous les projets. Aucune valeur RTK n'est recalculée ni complétée.
* **Marge** : jetons = octets / ratio ; octets = jetons RTK × 4 ; ratio bas 3, ratio haut 5 (hypothèses de l'auteur du script, à ajuster).
* **Non couvert** : coût en jetons des appels du compte gratuit, économies hors RTK, qualité comparée des réponses. Aucune de ces valeurs n'est estimée ici.
