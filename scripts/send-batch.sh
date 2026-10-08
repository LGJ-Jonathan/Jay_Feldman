#!/usr/bin/env bash
# Sends the staged give-first replies, one at a time, through send-approved.py.
#
# Every guard in send-approved.py still applies to every single send: the
# killswitch, the one-send-ever log, the automated_reply check, the live
# thread re-read, the daily cap. This script adds no send power of its own,
# it only saves you from pasting 19 commands.
#
# Usage:
#   BISON_API_KEY=... bash scripts/send-batch.sh deliver      # the 9 with a list
#   BISON_API_KEY=... bash scripts/send-batch.sh ask          # the 10 niche questions
#   BISON_API_KEY=... bash scripts/send-batch.sh deliver --dry-run
set -u
BUCKET="${1:?usage: send-batch.sh <deliver|ask> [--dry-run]}"; shift || true
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - "$BUCKET" <<'PY' > /tmp/give-first-batch.tsv
import json, sys
m = json.load(open("Leads/fulfillment/staged/manifest.json"))
for r in m[sys.argv[1]]:
    print(f"{r['reply_id']}\t{r.get('attachment') or ''}\t{r['first_name']} @ {r['company']}")
PY

total=$(wc -l < /tmp/give-first-batch.tsv | tr -d ' ')
echo "$BUCKET: $total staged"; echo
sent=0; refused=0
while IFS=$'\t' read -r rid attach who; do
  body="Leads/fulfillment/staged/${rid}.txt"
  [ -f "$body" ] || { echo "SKIP  $who (no staged body)"; continue; }
  args=(--reply-id "$rid" --body-file "$body")
  [ -n "$attach" ] && args+=(--attach "Leads/fulfillment/lists/${attach}")
  printf '%-44s ' "$who"
  if python3 scripts/send-approved.py "${args[@]}" "$@"; then sent=$((sent+1)); else refused=$((refused+1)); fi
  sleep 20
done < /tmp/give-first-batch.tsv

echo; echo "sent: $sent   refused: $refused"
echo "A refusal is the guard doing its job. Read the 'refused' field before retrying anything."
