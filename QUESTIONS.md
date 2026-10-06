# QUESTIONS — grappes

Statut au 2026-10-06, après `REPONSES_SEDNAL.md`. Aucune réponse inventée.

## Ouvertes

* **Q2** 2-3 exemples de JSON bruts anonymisés par écosystème (X, Telegram, web) ? Bloque la phase 7.
* **Q3** Langues des corpus ?
* **Q7b** Base légale du traitement : non précisée (la réponse de Sednal ne porte que sur `retention_days` et `redact_persons`, voir D20). À fournir avant toute donnée réelle.
* **Q10** Clients MCP visés et lieu d'exécution ?
* **Q11** Scoring par embeddings plus tard, oui ou non ?

## Réglées ou provisoires

* **Q7** Partiellement réglée (D20) : pas de `retention_days`, pas de `redact_persons`. Reste la base légale (Q7b).
* **Q15** Réglée (D19) : E vaut 0 tant que le recoupement n'est pas validé ; `explain` indique `recoupement_partiel`.
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
