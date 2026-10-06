# DECISIONS — grappes

| # | Date | Décision | Statut |
| --- | --- | --- | --- |
| D1 | 2026-10-06 | Plage 9 h à 17 h supprimée de MISSION.md par Sednal (D1 initial : §0 (fonctionnement continu, pas de plage horaire) prime sur la « plage 9 h à 17 h » du §4.2/§4.3, car §0 est marqué « remplace l'ancien ». Le hook n'implémentera donc pas la plage interdite, ). | prise |
| D2 | 2026-10-06 | Questions non posables dans l'issue (`gh` absent) : consignées dans `QUESTIONS.md`, pilotage par tmux. | prise |
| D3 | 2026-10-06 | Brouillons de migration (CLAUDE.md, continuer.sh, appeler_gratuit.sh) placés dans `docs/conception/migration_env.md`, pas dans `outils/`, pour ne rien activer avant accord. | prise |
| D4 | 2026-10-06 | Watchdog « session limit » (§4.4) : timer systemd qui détecte le message dans le pane tmux et envoie la reprise. Non implémenté avant le « go » (Q13). | proposée |
| D5 | 2026-10-06 | Dépôt git dédié initialisé dans `/opt/grappes` (nom de travail `grappes`, Q1 toujours ouverte). | prise |
