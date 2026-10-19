#!/bin/bash
# Compare les tokens Pro (local, sednal) vs Gratuit (OpenRouter/sednal-free) pour une date.
# Usage : comparer_tokens.sh [YYYY-MM-DD]
set -euo pipefail

DATE="${1:-$(date +%F)}"
OPENROUTER_KEY="${OPENROUTER_MANAGEMENT_KEY:?Variable OPENROUTER_MANAGEMENT_KEY non définie}"

# --- Côté Pro (sednal, transcripts locaux Claude Code) ---
PRO_JSON=$(npx ccusage@latest daily --json --since "$DATE" --until "$DATE" 2>/dev/null)
PRO_TOKENS=$(echo "$PRO_JSON" | jq '[.daily[]? | (.inputTokens + .outputTokens)] | add // 0')

# --- Côté gratuit (OpenRouter) ---
FREE_JSON=$(curl -s "https://openrouter.ai/api/v1/activity?date=$DATE" \
  -H "Authorization: Bearer $OPENROUTER_KEY")
FREE_TOKENS=$(echo "$FREE_JSON" | jq '[.data[]? | (.prompt_tokens + .completion_tokens)] | add // 0')

TOTAL=$((PRO_TOKENS + FREE_TOKENS))
PCT_FREE="0.0"
[ "$TOTAL" -gt 0 ] && PCT_FREE=$(awk "BEGIN{printf \"%.1f\", ($FREE_TOKENS/$TOTAL)*100}")

echo "=== Répartition tokens momo — $DATE ==="
echo "Pro (sednal)              : $PRO_TOKENS tokens"
echo "Gratuit (sednal-free/CCR) : $FREE_TOKENS tokens"
echo "Total                     : $TOTAL tokens"
echo "Part gratuite             : ${PCT_FREE}%"

# Historique
LOG="/opt/grappes/donnees/.economies_tokens.csv"
mkdir -p "$(dirname "$LOG")"
[ -f "$LOG" ] || echo "date,pro_tokens,free_tokens,total_tokens,pct_free" > "$LOG"
echo "$DATE,$PRO_TOKENS,$FREE_TOKENS,$TOTAL,$PCT_FREE" >> "$LOG"
