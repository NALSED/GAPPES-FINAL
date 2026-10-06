#!/bin/bash
# Hook Stop : force la continuation (exit 2) avec anti-boucle ; chemins relatifs au projet.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 0
mkdir -p "$ROOT/donnees"
ETAT_FILE="$ROOT/donnees/.stop_hook_state"
HEAD=$(git rev-parse HEAD 2>/dev/null || echo "none")
if [ -f "$ETAT_FILE" ]; then read -r LAST_HEAD COUNT < "$ETAT_FILE"; else LAST_HEAD=""; COUNT=0; fi
if [ "$HEAD" = "$LAST_HEAD" ]; then COUNT=$((COUNT+1)); else COUNT=0; fi
echo "$HEAD $COUNT" > "$ETAT_FILE"
[ "$COUNT" -ge 2 ] && exit 0
echo "Relis ETAT.md et ne traite que la phase en cours. Si un point est reellement bloquant (bug, decision irreversible), decris-le clairement et arrete-toi sur ce point precis." >&2
exit 2
