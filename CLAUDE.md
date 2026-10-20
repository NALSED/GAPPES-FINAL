# CLAUDE.md — grappes

* Documents de référence : `FINAL.md` (référence unique, prioritaire) puis `MISSION.md` (lecture seule pour l'agent) pour tout ce que `FINAL.md` ne traite pas. Les fichiers de `docs/archive/` sont obsolètes. Les relire en début de session.
* Mode continu : pas de plage horaire, pas de plafond ; l'agent tranche seul et trace chaque décision dans `DECISIONS.md`. Notification à Sednal uniquement en cas de bug bloquant.
* §2 : suivi dans `ETAT.md`, `DECISIONS.md`, `QUESTIONS.md`. Ambiguïté : l'écrire dans `QUESTIONS.md`, ne rien inventer. Fin de phase : tests verts, suivi à jour, puis phase suivante sans validation. Ne solliciter Sednal que pour un choix crucial ou un bug critique.
* Docs, commentaires et commits en français ; identifiants de code en anglais. Blocs de code des `.md` en quatre backticks. Petits commits, tests verts avant chaque commit.
* Routage §4.5 : tâches **mécaniques** (fixtures synthétiques, reformatage, `ruff`, docstrings, renommages) via :
  `outils/appeler_gratuit.sh "<description>" -- sudo -iu sednal-free bash -lc 'claude -p "<tâche>" --settings "{\"env\":{\"ANTHROPIC_MODEL\":\"OpenRouter/nvidia/nemotron-3-ultra-550b-a55b:free\"}}"'`
  Une commande purement locale sans IA (ruff seul, mv, etc.) ne passe pas par le wrapper : elle s'exécute directement, elle ne consomme aucun compte. Tâches de **jugement** (architecture, scoring, recoupement, revue, décisions) sur le compte Pro. Sous pression de quota, déplacer plus de mécanique vers le gratuit et le noter dans `ETAT.md`.
* rtk reste actif ; ne pas présenter `rtk gain` comme une économie totale. Si une troncature gêne, la consigner dans `QUESTIONS.md`.
* Aucun lexique réel : thèmes neutres inventés uniquement.
* Économie de jetons (2026-10-20) : tests par `PATH=<projet>/.venv/bin:$PATH rtk pytest -q …` (réussite en une ligne, échecs détaillés, sortie complète par `rtk recall <id>`) ; jamais de `ls`/`find` complet sur `donnees/autocal*` (milliers de fichiers : `| wc -l` ou `| head`) ; tenir la ligne « Phase en cours : … » en tête d'`ETAT.md` (le hook d'arrêt ne relance que si une phase est en cours).
