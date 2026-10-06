# QUESTIONS — grappes

Statut au 2026-10-06, après `REPONSES_SEDNAL.md`. Aucune réponse inventée.

## Ouvertes

* **Q2** 2-3 exemples de JSON bruts anonymisés par écosystème (X, Telegram, web) ? Bloque la phase 7.
* **Q3** Langues des corpus ?
* **Q7** Base légale, `retention_days`, `redact_persons` par défaut ? Bloque la phase 7 : aucune donnée réelle n'est ingérée avant la réponse.
* **Q10** Clients MCP visés et lieu d'exécution ?
* **Q11** Scoring par embeddings plus tard, oui ou non ?
* **Q15** (nouvelle) Avec la formule D15, E compte même quand le recoupement est **refusé** (E se calcule sur les citants membres, pas sur `validated`). Exemple du corpus synthétique : `x:cible_mono_eco`, citée par 5 membres de la grappe A d'un seul écosystème, est refusée (`écosystèmes 1 < 2`) mais obtient E = 83, donc confiance 50 ≥ `seuil_min` : classée « probable », `via = semantique`. Avec l'ancienne formule (0,3·E), elle restait à 25, non classée. Faut-il (a) garder ce comportement, (b) ne compter E que si le recoupement est validé, ou (c) afficher `via = recoupement_partiel` pour ne pas l'attribuer à la sémantique ? Comportement actuel conservé (conforme à la formule fournie).

## Réglées ou provisoires

* **Q1** Réglée : « grappes » reste le nom de travail.
* **Q4, Q5, Q9** Valeurs actuelles gardées (seuils par défaut ; CSV `;`, UTF-8 sans BOM ; règle d'opposition par marge). Provisoire, à recalibrer avec des données réelles.
* **Q6** Thèmes neutres de démonstration conservés (cuisine, jardinage).
* **Q8** Sans objet (plage horaire supprimée).
* **Q12** Réglée : hook `Stop` migré et vérifié.
* **Q13** Pas de watchdog pour l'instant (D4 reste « proposée »). Chaque interruption « session limit » est notée dans `ETAT.md`.
* **Q14** Classification mécanique / jugement validée ; N = 5, atteint (8 lignes dans le journal).
* **QA** Confirmé : on suit `MISSION.md` (`grappes`).
* **QB** Réglée : hook `Stop` vers `/opt/grappes/outils/continuer.sh`.
* **QC** Réglée : pas de phase 7 « données réelles » tant que Q2 et Q7 n'ont pas de réponse.
* Q12 à Q14 manquent dans le §17 de `MISSION.md` : Sednal les ajoute (je ne touche pas à `MISSION.md`).
