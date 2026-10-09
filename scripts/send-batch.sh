#!/usr/bin/env bash
# Sends staged give-first replies, one at a time, through send-approved.py.
#
# This script adds no send power of its own. Every single send still passes
# every guard in send-approved.py: the killswitch, the one-send-ever log, the
# automated_reply check, the live thread re-read, the gift-code placeholder
# check, the daily cap. A refusal here is a guard working, not a failure.
#
# Usage:
#   BISON_API_KEY=... bash scripts/send-batch.sh ready            # everything with nothing missing
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
case " $* " in
  *" --dry-run "*) echo "$WHICH: $total staged. Dry run, nothing will be sent." ;;
  *) echo "$WHICH: $total staged. SENDING now. Ctrl-C stops it." ;;
esac
echo
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
  # Each lead's thread belongs to its own mailbox: this batch is 20 leads across
  # 20 distinct sender mailboxes, one email each, so there is no per-mailbox
  # burst to space out and the old 20s pause bought nothing. A short pause is
  # kept only to stay polite to the API. Override with GIVE_FIRST_PAUSE.
  case " $* " in *" --dry-run "*) : ;; *) sleep "${GIVE_FIRST_PAUSE:-2}" ;; esac
done < /tmp/give-first-queue.tsv

echo; echo "sent: $sent   refused: $refused"
echo "Read the 'refused' field on anything that did not go. Never re-run a send that"
echo "returned sent:true, the Bison endpoint is not idempotent."
