# DECISIONS — grappes

| # | Date | Décision | Statut |
| --- | --- | --- | --- |
| D1 | 2026-10-06 | Plage 9 h à 17 h supprimée de MISSION.md par Sednal (D1 initial : §0 (fonctionnement continu, pas de plage horaire) prime sur la « plage 9 h à 17 h » du §4.2/§4.3, car §0 est marqué « remplace l'ancien ». Le hook n'implémentera donc pas la plage interdite, ). | prise |
| D2 | 2026-10-06 | Questions non posables dans l'issue (`gh` absent) : consignées dans `QUESTIONS.md`, pilotage par tmux. | prise |
| D3 | 2026-10-06 | Brouillons de migration (CLAUDE.md, continuer.sh, appeler_gratuit.sh) placés dans `docs/conception/migration_env.md`, pas dans `outils/`, pour ne rien activer avant accord. | prise |
| D4 | 2026-10-06 | Watchdog « session limit » (§4.4) : timer systemd qui détecte le message dans le pane tmux et envoie la reprise. Non implémenté avant le « go » (Q13). | proposée |
| D5 | 2026-10-06 | Dépôt git dédié initialisé dans `/opt/grappes` (nom de travail `grappes`, Q1 toujours ouverte). | prise |
| D6 | 2026-10-06 | Pleine autonomie : `ATTENTE_VALIDATION` et STOP de fin de phase supprimés (MISSION §0/§2.2 modifiés par Sednal). Sollicitation uniquement pour choix crucial ou bug critique. | prise |
| D7 | 2026-10-06 | §9.1 : la formule `100 × (1 − exp(−raw/scale))` avec `scale = 3` donne 63,2 pour trois termes de poids 1, pas ≈ 86 comme annoncé (86,5 correspond à `scale = 1,5`). On garde la formule et `scale = 3.0` (valeur initiale configurable par grappe) ; test écrit sur la formule. À réviser si Sednal préfère `scale = 1,5`. | prise |
| D8 | 2026-10-06 | `normalize` recompose en NFC après retrait des accents latins, pour que « й » ne reste pas décomposé. | prise |
| D9 | 2026-10-06 | Phase 3 : confiance = S seule (E = A = 0 jusqu'à la phase 4) ; entités = sources vues + éléments cités (mentions → `ecosystème:handle`, liens → `web:domaine`) ; `run_id` = hash(config_hash + obs_id triés) pour des exports rejouables ; CSV `;`, UTF-8 sans BOM (configurable). | prise |
| D10 | 2026-10-06 | Le schéma SQL est dupliqué dans `storage/db.py` (exécuté) et `docs/conception/schema.sql` (doc) ; `observations` a 4 colonnes en plus du §10.3 (mentions, links, hashtags, engagement) pour rejouer `run` sans les JSON d'origine. | prise |
