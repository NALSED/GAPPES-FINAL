# Migration d'environnement (§4.2) — brouillons non actifs

Rien ici n'est appliqué. Chaque étape attend la validation de Sednal.

## Plan

1. Dépôt git et `/opt/<projet>` avec `outils/` et `donnees/` (Q1).
2. `CLAUDE.md` (brouillon ci-dessous).
3. `outils/continuer.sh` patché depuis `/opt/mapping/outils/continuer.sh`.
4. `outils/appeler_gratuit.sh` et `donnees/.journal_ccr.log`.
5. `~/.claude/settings.json` : sauvegarde `settings.json.bak-AAAAMMJJ`, puis remplacement du hook `Stop` (un seul actif).
6. Nouvelle session tmux dans le nouveau projet.
7. Checklist §4.7.

## Brouillon `CLAUDE.md`

````markdown
# CLAUDE.md — grappes
* Document de référence : `MISSION.md` (lecture seule, prime sur tout).
* Rappel §2 : suivi dans ETAT/DECISIONS/QUESTIONS ; ambiguïté -> QUESTIONS.md, ne rien inventer ; fin de phase -> tests verts, ATTENTE_VALIDATION, STOP.
* Docs/commits en français, code en anglais ; blocs de code en quatre backticks dans les .md.
* Routage §4.5 : tâches mécaniques (fixtures, reformatage, ruff, docstrings, renommages) via `outils/appeler_gratuit.sh "<description>" -- <commande>` ; jugement (architecture, scoring, recoupement, revue) sur le compte Pro.
* rtk reste actif ; ne pas contourner une troncature, la consigner dans QUESTIONS.md.
````

## Brouillon `outils/continuer.sh`

````bash
#!/bin/bash
# Chemin relatif au script, jamais code en dur vers un autre projet.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 0
# STOP de fin de phase
[ -f "$ROOT/ATTENTE_VALIDATION" ] && exit 0
ETAT_FILE="$ROOT/donnees/.stop_hook_state"
HEAD=$(git rev-parse HEAD)
if [ -f "$ETAT_FILE" ]; then read -r LAST_HEAD COUNT < "$ETAT_FILE"; else LAST_HEAD=""; COUNT=0; fi
if [ "$HEAD" = "$LAST_HEAD" ]; then COUNT=$((COUNT+1)); else COUNT=0; fi
echo "$HEAD $COUNT" > "$ETAT_FILE"
[ "$COUNT" -ge 2 ] && exit 0
echo "Relis ETAT.md et ne traite que la phase en cours. Si un point est reellement bloquant (bug, decision irreversible), decris-le et arrete-toi." >&2
exit 2
````

La plage 9 h à 17 h n'est pas incluse (D1, Q8).

## Brouillon `outils/appeler_gratuit.sh`

````bash
#!/bin/bash
# Usage : outils/appeler_gratuit.sh "<description>" -- <commande>
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DESCRIPTION="$1"; shift; shift
mkdir -p "$ROOT/donnees"
echo "$(date -Iseconds) | $DESCRIPTION" >> "$ROOT/donnees/.journal_ccr.log"
exec "$@"
````
