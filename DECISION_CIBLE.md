# DECISION_CIBLE — décision de Sednal (recopiée telle quelle le 2026-10-13)

Numérotation : Sednal l'appelle « D69 » ; numéro libre suivant dans `DECISIONS.md`.

Décision D69. Écris-la dans DECISION_CIBLE.md, commit, puis applique.

POURQUOI. La tâche que fait grappes est une tâche de recherche connue : "entity
list completion", évaluée par le NIST (TREC Entity Track 2010 et 2011) puis sur
DBpedia-Entity v2. Meilleurs scores mondiaux publiés : R-précision 0,31 (TREC 2010),
0,29 (TREC 2011, piste suspendue en 2012), nDCG@10 0,44 (2017), 0,54 (2022), 0,52
(2025). Le critère de 0,90 était donc hors d'atteinte pour quiconque. Vérifie ces
chiffres toi-même et dis-le dans le document si tu trouves autre chose.

1. DEUX CIBLES AU LIEU D'UNE. Classe chaque sujet avant toute mesure, sur la seule
phrase du sujet, comme pour la ligne B :
   - acteurs présents dans un registre officiel français (associations déclarées,
     sociétés, classements ou labels officiels) : cible R-précision >= 0,90 ;
   - pas de liste faisant autorité (catégories ouvertes, acteurs informels) :
     cible 0,30 à 0,40, soit le niveau de l'état de l'art mondial, et dis-le.
   Les deux cibles sont rendues séparément, jamais fusionnées.

2. VÉRIFICATEUR DE TYPE. C'est ce qui a fait gagner Purdue à TREC 2010 : avant de
classer un candidat, vérifier que son type correspond au type demandé. Implémente-le.
C'est la réponse à mon point "filtrer le bruit" : on ne filtre pas après coup, on
vérifie le type en amont. Mesure l'effet sur les 2 063 candidats en trop, en
particulier les 242 entrepreneurs de spectacles arrivés sur le handball.

3. AMORCES. Dans la définition TREC, le système reçoit 2 à 23 entités connues comme
exemples de départ. Personne dans la recherche ne part d'une phrase seule. Mesure,
sans rien activer, le gain qu'apporteraient 3 exemples fournis en entrée. Si le gain
est net, je déciderai d'en faire une entrée du produit.

4. MES RÉPONSES À TES QUESTIONS D68 :
   - poids registre_source : garde 0,19, ne le règle pas sur six sujets ;
   - bruit : voir le point 2, pas de filtre inventé ;
   - validation : oui, mesure les prises data.gouv.fr sur la validation, j'ai besoin
     de savoir si le gain de +2 points est réel ou un ajustement aux six sujets ;
   - autres leviers : n'en ouvre aucun ;
   - certification : toute nouvelle tentative suppose un nouveau jeu test, nouvelle
     graine, figé avant toute modification.

AUTONOMIE inchangée : tu remontes sans appliquer tout changement de format de
resultat.csv, toute suppression de données, toute activation des personnes,
min_ecosystemes sous 2, toute réouverture du jeu test.
