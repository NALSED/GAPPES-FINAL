# QUESTIONS — grappes

Statut : ouvertes sauf mention. Aucune réponse inventée.

* **Q1** Nom définitif du projet et du dépôt (nom de travail `grappes`) ?
* **Q2** 2-3 exemples de JSON bruts par écosystème (X, Telegram, web) ?
* **Q3** Langues des corpus ?
* **Q4** Valeurs initiales : `min_citers`, écosystèmes minimum, `crossref_floor`, `seuil_min`, `marge_ambiguïté` ?
* **Q5** CSV : séparateur `;`, UTF-8, BOM pour Excel ?
* **Q6** Grappes de démonstration : thèmes neutres choisis par momo, OK ?
* **Q7** Base légale, `retention_days`, `redact_persons` par défaut ?
* **Q8** Sans objet (plage horaire supprimée).
* **Q9** Règle d'opposition par marge (§9.4) acceptée ?
* **Q10** Clients MCP visés et lieu d'exécution ?
* **Q11** Scoring par embeddings plus tard, oui ou non ?
* **Q12 à Q14** : citées dans `MISSION.md` (Q12 qui exécute les étapes 5 et 6, Q13 watchdog, Q14 classification mécanique/jugement et N lignes de journal) mais absentes du §17. À fournir.
* **QA** Le premier message parlait de « mapping / sites abandonnés » ; je suis `MISSION.md` (`grappes`). Confirmé implicitement par la mise à jour de `MISSION.md` ; à infirmer si faux.
* **QB** Édition de `~/.claude/settings.json` (hook `Stop` → `/opt/grappes/outils/continuer.sh`) refusée par le classifieur : à faire par Sednal (`sed -i` après sauvegarde), ou autorisation explicite via une règle de permission.
