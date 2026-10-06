# CLAUDE.md — grappes

* Document de référence : `MISSION.md` (lecture seule pour l'agent, prime sur tout). Le relire en début de session.
* Mode continu : pas de plage horaire, pas de plafond ; l'agent tranche seul et trace chaque décision dans `DECISIONS.md`. Notification à Sednal uniquement en cas de bug bloquant.
* §2 : suivi dans `ETAT.md`, `DECISIONS.md`, `QUESTIONS.md`. Ambiguïté : l'écrire dans `QUESTIONS.md`, ne rien inventer. Fin de phase : tests verts, suivi à jour, puis phase suivante sans validation. Ne solliciter Sednal que pour un choix crucial ou un bug critique.
* Docs, commentaires et commits en français ; identifiants de code en anglais. Blocs de code des `.md` en quatre backticks. Petits commits, tests verts avant chaque commit.
* Routage §4.5 : tâches **mécaniques** (fixtures synthétiques, reformatage, `ruff`, docstrings, renommages) via `outils/appeler_gratuit.sh "<description>" -- <commande>` ; tâches de **jugement** (architecture, scoring, recoupement, revue, décisions) sur le compte Pro. Sous pression de quota, déplacer plus de mécanique vers le gratuit et le noter dans `ETAT.md`.
* rtk reste actif ; ne pas présenter `rtk gain` comme une économie totale. Si une troncature gêne, la consigner dans `QUESTIONS.md`.
* Aucun lexique réel : thèmes neutres inventés uniquement.
