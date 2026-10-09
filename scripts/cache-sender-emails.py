#!/usr/bin/env python3
"""
Caches every live sending mailbox in the workspace to scripts/sender-emails.json.

The sender needs this when a reply carries no sender_email_id: the mailbox the
lead replied TO is ours, named in primary_to_email_address, and this map turns
that address into the id the reply endpoint wants.

It also shows when a mailbox has been removed from the workspace, which is not
recoverable: a thread opened from a mailbox that no longer exists cannot be
answered from it.

  BISON_API_KEY=... python3 scripts/cache-sender-emails.py
"""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "sender-emails.json"
KEY = os.environ.get("BISON_API_KEY", "")


def main():
    if not KEY:
        sys.exit("BISON_API_KEY is empty. It holds a '|', so quote it: "
                 "export BISON_API_KEY='674|...'")
    by_email, page = {}, 1
    while page <= 60:
        req = urllib.request.Request(
            f"https://send.leadgenjay.com/api/sender-emails?page={page}",
            headers={"Authorization": "Bearer " + KEY})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                rows = json.load(r).get("data") or []
        except urllib.error.HTTPError as e:
            sys.exit(f"Bison returned {e.code} on page {page}"
                     + (" (check the key is quoted)" if e.code in (401, 403) else ""))
        if not rows:
            break
        for row in rows:
            email = (row.get("email") or "").lower()
            if email:
                by_email[email] = row.get("id")
        page += 1
    OUT.write_text(json.dumps({
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "by_email": by_email}, indent=1) + "\n")
    print(f"{len(by_email)} live mailboxes cached to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
