# Test de charge

Commande : `.venv/bin/python outils/charge.py 100000 <dossier>` (observations synthétiques, thèmes neutres, 5 000 sources, 3 écosystèmes, 0 à 2 citations par observation).

Mesure du 2026-10-06 (VM de développement, Python 3.13) :

| Étape | Durée |
| --- | --- |
| Insertion SQLite | 1,3 s |
| Chargement | 0,6 s |
| Scoring + recoupement + affectation (2 itérations) | 2,7 s |
| Sauvegarde du run | 0,3 s |
| Export CSV | < 0,1 s |
| **Total** | **5,0 s** |

Pic mémoire : environ 200 Mo ; base SQLite : 33 Mo. 6 666 entités, 100 246 citations, 10 000 enregistrements de validation.

Ces chiffres valent pour les lexiques de démonstration (2 grappes, quelques termes) ; le coût croît avec le nombre de grappes et de termes.
