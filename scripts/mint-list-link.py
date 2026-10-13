#!/usr/bin/env python3
"""
Mints a download link for one list, for one prospect.

Why not Google Drive: a Drive link is either private (the prospect cannot open
it) or public (3,944 contacts reachable by URL forever). A token on our own host
is neither. Each link names one list and one prospect, can be expired, and the
server records when it is fetched, so we know whether a lead actually took the
list.

  python3 scripts/mint-list-link.py --reply-id 6970644 \
      --list manufacturing-companies.csv --email rkohl@kkominc.com

Prints the URL to put in the reply. Re-minting for the same reply and list
returns the existing token rather than a second one.
"""
import argparse, json, os, secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTS = ROOT / "Leads" / "fulfillment" / "lists"
TOKENS = ROOT / "scripts" / "list-tokens.json"
BASE = os.environ.get("LIST_LINK_BASE", "https://files.nextwave.io")
TTL_DAYS = int(os.environ.get("LIST_LINK_TTL_DAYS", "90"))


def load():
    try:
        return json.loads(TOKENS.read_text())
    except Exception:
        return {"tokens": {}}


def save(d):
    tmp = TOKENS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(d, indent=1))
    tmp.replace(TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reply-id", required=True)
    ap.add_argument("--list", required=True, help="file name inside Leads/fulfillment/lists")
    ap.add_argument("--email", required=True)
    ap.add_argument("--rows", type=int, help="rows promised, recorded for the audit trail")
    a = ap.parse_args()

    csv = LISTS / a.list
    if not csv.is_file():
        raise SystemExit(f"no such list: {a.list}")

    db = load()
    for tok, rec in db["tokens"].items():
        if rec["reply_id"] == str(a.reply_id) and rec["list"] == a.list and not rec.get("revoked"):
            print(f"{BASE}/d/{tok}")
            return

    tok = secrets.token_urlsafe(18)
    db["tokens"][tok] = {
        "reply_id": str(a.reply_id), "list": a.list, "email": a.email,
        "rows": a.rows, "minted": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "expires": (datetime.now(timezone.utc) + timedelta(days=TTL_DAYS)).isoformat(timespec="seconds"),
        "fetches": [],
    }
    save(db)
    print(f"{BASE}/d/{tok}")


if __name__ == "__main__":
    main()
