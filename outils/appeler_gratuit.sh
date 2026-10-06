#!/bin/bash
# Journalise chaque appel au compte gratuit (sednal-free / CCR) avant de l'executer.
# Usage : outils/appeler_gratuit.sh "<description courte>" -- <commande complete>
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DESCRIPTION="$1"
shift
shift  # retire le separateur --
mkdir -p "$ROOT/donnees"
echo "$(date -Iseconds) | $DESCRIPTION" >> "$ROOT/donnees/.journal_ccr.log"
exec "$@"
