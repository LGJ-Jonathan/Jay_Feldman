#!/usr/bin/env python3
"""
Sends ONE approved give-first reply, in thread, with the list attached.

This is the only script in the repo that can email a prospect. Everything about
it is built so it cannot be the second email a lead receives:

  - it refuses if scripts/sender.off exists (killswitch)
  - it refuses a reply id already in scripts/sent-log.json (one send, ever)
  - it re-fetches the reply and refuses if it is an automated_reply
  - it re-reads the conversation thread immediately before sending and refuses
    if ANYONE has already answered. A replier is live on this workspace that
    answers as "Amy" within minutes, so this check is the real guard, not a
    formality.
  - it refuses an unsubstituted {{GIFT_CODE}} placeholder, so no lead gets a
    literal token where their gift link should be
  - it refuses past a daily cap
  - it NEVER retries the POST. The endpoint is not idempotent and a retry
    re-mails the prospect.

Usage:
  BISON_API_KEY=... python3 scripts/send-approved.py \
      --reply-id 6835890 --body-file /tmp/body.txt \
      [--attach Leads/fulfillment/lists/ecommerce-brands.csv] [--dry-run]

Prints one JSON object. "sent": true only when Bison returned a new reply id.
"""
import argparse, json, mimetypes, os, sys, urllib.request, urllib.error, uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://send.leadgenjay.com/api"
KEY = os.environ.get("BISON_API_KEY", "")
OFF = ROOT / "scripts" / "sender.off"
LOG = ROOT / "scripts" / "sent-log.json"
DAILY_CAP = int(os.environ.get("GIVE_FIRST_DAILY_CAP", "25"))
MAX_BODY = 1500


def out(**kw):
    print(json.dumps(kw))
    sys.exit(0 if kw.get("sent") or kw.get("dry_run") else 1)


def get(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def load_log():
    return json.loads(LOG.read_text()) if LOG.exists() else {"sent": []}


def multipart(fields, filepath):
    """Build a multipart/form-data body. attachments[] must be a real file."""
    b = uuid.uuid4().hex
    parts = []
    for k, v in fields:
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    if filepath:
        name = Path(filepath).name
        ctype = mimetypes.guess_type(name)[0] or "text/csv"
        parts.append(
            f"--{b}\r\nContent-Disposition: form-data; name=\"attachments[0]\"; "
            f"filename=\"{name}\"\r\nContent-Type: {ctype}\r\n\r\n".encode()
            + Path(filepath).read_bytes() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={b}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reply-id", type=int, required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--attach")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not KEY:
        out(sent=False, refused="BISON_API_KEY not set")
    if OFF.exists():
        out(sent=False, refused="killswitch: scripts/sender.off exists")

    log = load_log()
    if any(s["reply_id"] == a.reply_id for s in log["sent"]):
        out(sent=False, refused="already sent once; one send per reply id, ever")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if sum(1 for s in log["sent"] if s["at"].startswith(today)) >= DAILY_CAP:
        out(sent=False, refused=f"daily cap of {DAILY_CAP} reached")

    body = Path(a.body_file).read_text().strip()
    if "{{GIFT_CODE}}" in body:
        out(sent=False, refused="body still has the {{GIFT_CODE}} placeholder; claim a code first")
    if not body:
        out(sent=False, refused="body is empty")
    if len(body) > MAX_BODY:
        out(sent=False, refused=f"body is {len(body)} chars, over the {MAX_BODY} limit")

    r = get(f"/replies/{a.reply_id}")
    if not r:
        out(sent=False, refused="reply not found")
    rep = r.get("data", r)
    if rep.get("automated_reply"):
        out(sent=False, refused="this is an automated reply; never answer one")

    lead_email = rep.get("from_email_address")
    sender_id = rep.get("sender_email_id")
    if not lead_email or not sender_id:
        out(sent=False, refused="reply is missing from_email_address or sender_email_id")

    # The guard that matters: has anyone answered since the lead wrote in?
    th = get(f"/replies/{a.reply_id}/conversation-thread")
    newer = (th or {}).get("data", th or {}).get("newer_messages") or []
    already = [m for m in newer if m.get("type") == "Outgoing Email"]
    if already:
        out(sent=False, refused="thread was already answered; sending would be a second email",
            answered_at=(already[0].get("date_received") or "")[:19])

    if a.attach:
        p = Path(a.attach)
        if not p.is_absolute():
            p = ROOT / p
        if not p.exists():
            out(sent=False, refused=f"attachment not found: {a.attach}")
        a.attach = str(p)

    if a.dry_run:
        out(sent=False, dry_run=True, would_send_to=lead_email, sender_email_id=sender_id,
            attachment=Path(a.attach).name if a.attach else None, body_chars=len(body))

    fields = [("message", body), ("sender_email_id", str(sender_id)),
              ("to_emails[0][email_address]", lead_email)]
    data, ctype = multipart(fields, a.attach)
    req = urllib.request.Request(f"{BASE}/replies/{a.reply_id}/reply", data=data, method="POST",
                                 headers={"Authorization": "Bearer " + KEY,
                                          "Content-Type": ctype, "Accept": "application/json"})
    # No retry. Ever. A retry re-mails the prospect.
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.load(resp)
    except urllib.error.HTTPError as e:
        out(sent=False, refused=f"HTTP {e.code}", detail=e.read()[:400].decode("utf8", "replace"))

    body_res = res.get("data", res)
    new_id = (body_res.get("reply") or {}).get("id") or body_res.get("id")
    log["sent"].append({"reply_id": a.reply_id, "new_reply_id": new_id, "to": lead_email,
                        "attachment": Path(a.attach).name if a.attach else None,
                        "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    LOG.write_text(json.dumps(log, indent=1) + "\n")
    out(sent=True, reply_id=a.reply_id, new_reply_id=new_id, to=lead_email,
        attachment=Path(a.attach).name if a.attach else None)


if __name__ == "__main__":
    main()
