#!/usr/bin/env bash
# Sends staged give-first replies, one at a time, through send-approved.py.
#
# This script adds no send power of its own. Every single send still passes
# every guard in send-approved.py: the killswitch, the one-send-ever log, the
# automated_reply check, the live thread re-read, the gift-code placeholder
# check, the daily cap. A refusal here is a guard working, not a failure.
#
# Usage:
#   BISON_API_KEY=... bash scripts/send-batch.sh ready            # the 19 with nothing missing
#   BISON_API_KEY=... bash scripts/send-batch.sh gated            # the 10 that need a gift code
#   BISON_API_KEY=... bash scripts/send-batch.sh all
#   BISON_API_KEY=... bash scripts/send-batch.sh ready --dry-run  # prove it first
set -u
WHICH="${1:?usage: send-batch.sh <ready|gated|all> [--dry-run]}"; shift || true
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PLAN="Leads/fulfillment/staged/send-plan.json"
[ -f "$PLAN" ] || { echo "no send plan at $PLAN"; exit 1; }

python3 - "$WHICH" "$PLAN" <<'PY' > /tmp/give-first-queue.tsv
import json, sys
which, plan = sys.argv[1], sys.argv[2]
p = json.load(open(plan))
keys = {"ready": ["ready"], "gated": ["needs_gift_code"],
        "all": ["ready", "needs_gift_code"]}[which]
att = {int(k): v for k, v in p["attachments"].items() if v}
for k in keys:
    for rid in p[k]:
        print(f"{rid}\t{att.get(int(rid), '')}")
PY

total=$(wc -l < /tmp/give-first-queue.tsv | tr -d ' ')
echo "$WHICH: $total staged"; echo
sent=0; refused=0
while IFS=$'\t' read -r rid attach; do
  body="Leads/fulfillment/staged/${rid}.txt"
  [ -f "$body" ] || { echo "SKIP  $rid (no staged body)"; continue; }
  args=(--reply-id "$rid" --body-file "$body")
  [ -n "$attach" ] && args+=(--attach "Leads/fulfillment/lists/${attach}")
  printf 'reply %-9s ' "$rid"
  res=$(python3 scripts/send-approved.py "${args[@]}" "$@"); rc=$?
  echo "$res"
  if [ $rc -eq 0 ]; then sent=$((sent+1)); else refused=$((refused+1)); fi
  # A bad key fails identically on every lead. Stop rather than repeat it 23 times.
  case "$res" in
    *'"auth_failed": true'*)
      echo; echo "Stopping: Bison rejected the key, so every remaining lead would fail the same way."
      echo "Fix the key and re-run. Nothing was sent."; exit 1 ;;
  esac
  sleep 20
done < /tmp/give-first-queue.tsv

echo; echo "sent: $sent   refused: $refused"
echo "Read the 'refused' field on anything that did not go. Never re-run a send that"
echo "returned sent:true, the Bison endpoint is not idempotent."
