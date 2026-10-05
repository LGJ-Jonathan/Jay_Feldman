#!/usr/bin/env python3
"""
Give-First fulfillment sweep — PREPARES, NEVER SENDS.

Sweeps the allowlisted Bison campaigns for interested replies that have not been
fulfilled yet, resolves each lead's client niche, picks or flags the list to deliver,
and writes an approval batch for a human to review.

This script has no send capability by design. The only runtime allowed to email a
prospect is Hermes on Bob (see consulti-give-first-fulfillment.md). It makes GET and
PATCH-free, read-only calls to Bison. If you ever feel the urge to add a POST to
/replies/{id}/reply here, don't: that creates a second replier.

Usage:
  BISON_API_KEY=... python3 scripts/fulfillment-sweep.py [--limit N]
"""
import json, os, sys, csv, time, shutil, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://send.leadgenjay.com/api"
KEY = os.environ.get("BISON_API_KEY", "")

ALLOWLIST = {
    1298: ("Blitz Agencies - Give-First 2 (9/26) Shara - Optimized", "signal_topic"),
    1313: ("Clutch Agencies - (coworker-9/26) Shara - Optimized", "niche"),
    1315: ("Clutch Agencies - (9/26) Shara - Optimized", "niche"),
    1145: ("Consulti Agencies - Give-First (8/22) Shara - optimizations", None),
}
NICHE_CHAIN = ["signal_topic", "niche", "industry", "client_niche"]
MIN_ROWS = 150

OUT = ROOT / "Leads" / "fulfillment"
LISTS = OUT / "lists"
STATE = ROOT / "scripts" / "fulfillment-state.json"  # in-repo: reply ids only, no PII, so
#                                                      dedupe survives cloud runs


def api(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503):
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    return None


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"handled_reply_ids": [], "batches": []}


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def clean_reply(body):
    """The lead's own words, without the quoted thread underneath."""
    out = []
    for line in body.splitlines():
        t = line.strip()
        if t.startswith(">"):
            break
        if t.lower().startswith(("on ", "from:", "-----original")) and "wrote:" in t.lower():
            break
        out.append(line)
    return "\n".join(out).strip()[:1500]


def resolve_niche(lead):
    cv = {c["name"]: (c.get("value") or "").strip()
          for c in (lead.get("custom_variables") or [])}
    for key in NICHE_CHAIN:
        if cv.get(key):
            return key, cv[key], cv
    return None, None, cv


def classify(niche, nmap):
    if not niche:
        return "no_niche", None
    k = niche.lower().strip()
    for cls in ("industry", "geo", "intent"):
        if k in nmap.get(cls, {}):
            return cls, nmap[cls][k]
    return "unmapped", None


DELIVERY_DRAFT = """Hi {first_name},

Here it is, attached. {rows} verified contacts at {niche}, with {columns} for each one.

It's yours to use however you like, for your own outreach or a client's. No strings.

If it's useful and you'd rather pull your own whenever a client launch comes up, I can gift you a month of Consulti so you can do it yourself in a few clicks.

Anything you'd want cut differently, just say so and I'll redo it.
"""

QUESTION_DRAFT = """Hi {first_name},

Happy to pull it.

What kind of businesses do you want them to be? Give me the industry and a city or state if it matters, and I'll put the list together and send it over.
"""


def main():
    if not KEY:
        sys.exit("BISON_API_KEY not set. Export it and re-run.")
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    nmap = json.loads((ROOT / "consulti-niche-filter-map.json").read_text())
    state = load_state()
    handled = set(state["handled_reply_ids"])

    found = []
    for cid, (name, _) in ALLOWLIST.items():
        page = 1
        while True:
            d = api(f"/campaigns/{cid}/replies?status=interested&per_page=15&page={page}")
            if not d or not d["data"]:
                break
            for r in d["data"]:
                if r["id"] in handled or r.get("automated_reply"):
                    continue
                lead = r.get("lead") or {}
                if not lead.get("id"):
                    continue
                found.append({"campaign": name, "campaign_id": cid, "reply_id": r["id"],
                              "lead_id": lead["id"], "email": lead.get("email"),
                              "first_name": lead.get("first_name"), "company": lead.get("company"),
                              "received": r.get("date_received"),
                              "reply_text": clean_reply(r.get("text_body") or "")})
            total = d.get("meta", {}).get("total", 0)
            if page * 15 >= total:
                break
            page += 1

    if limit:
        found = found[:limit]
    if not found:
        print("No new interested replies. Nothing to approve.")
        return

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    batch = OUT / f"batch-{stamp}"
    (batch / "attachments").mkdir(parents=True, exist_ok=True)
    (batch / "drafts").mkdir(parents=True, exist_ok=True)

    rows = []
    for f in found:
        lead = api(f"/leads/{f['lead_id']}")
        if not lead:
            continue
        src, niche, cv = resolve_niche(lead["data"])
        cls, spec = classify(niche, nmap)
        f.update(niche=niche, niche_source=src, cls=cls)

        attach = None
        note = ""
        if cls == "industry":
            src_file = LISTS / f"{slug(niche)}.csv"
            if src_file.exists():
                n = sum(1 for _ in open(src_file)) - 1
                if n < MIN_ROWS:
                    note = f"BLOCKED: cached list has only {n} rows, floor is {MIN_ROWS}"
                else:
                    attach = f"{slug(niche)}.csv"
                    shutil.copy(src_file, batch / "attachments" / attach)
                    hdr = open(src_file).readline().strip().split(",")
                    pretty = {"first_name": "name", "last_name": None, "title": "title",
                              "company": "company", "linkedin_url": "LinkedIn",
                              "website": "website", "phone": "phone", "city": "city",
                              "state": None, "email": "a verified email"}
                    cols = [pretty[h] for h in hdr if pretty.get(h)]
                    columns = ", ".join(cols[:-1]) + " and " + cols[-1]
                    draft = DELIVERY_DRAFT.format(first_name=f["first_name"] or "there",
                                                  rows=n, niche=niche, columns=columns)
            else:
                note = f"NEEDS LIST BUILD: no cached file at lists/{slug(niche)}.csv"
        elif cls == "geo":
            note = "NEEDS PER-LEAD BUILD: geo niche, requires their city/state and a Consulti pull"
        elif cls == "intent":
            note = "ASK: niche is a buying signal, not an industry. No list exists for it"
        elif cls == "no_niche":
            note = "ASK: no niche variable on this lead (campaign 1145 never set one)"
        else:
            note = f"UNMAPPED niche '{niche}'. Add it to consulti-niche-filter-map.json"

        if not attach:
            draft = QUESTION_DRAFT.format(first_name=f["first_name"] or "there")

        dpath = batch / "drafts" / f"{f['reply_id']}.txt"
        dpath.write_text(draft)
        f.update(attachment=attach, note=note, draft=draft,
                 draft_file=str(dpath.relative_to(batch)))
        rows.append(f)

    ready = [r for r in rows if r["attachment"]]
    ask = [r for r in rows if not r["attachment"] and r["cls"] in ("intent", "no_niche")]
    blocked = [r for r in rows if not r["attachment"] and r["cls"] not in ("intent", "no_niche")]

    lines = [f"# Fulfillment batch {stamp} — awaiting approval", "",
             f"{len(rows)} new interested replies. **Nothing has been sent.** This script cannot send.",
             "", f"- {len(ready)} ready to send with a list attached",
             f"- {len(ask)} get the clarifying question instead (no list exists for their niche)",
             f"- {len(blocked)} blocked, needs a list built first", "",
             "Approve by replying to Claude with the reply ids you approve, or `all`.", "",
             "| Reply id | Lead | Company | Niche | Source | Class | Attachment | Note |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['reply_id']} | {r['first_name']} <{r['email']}> | {r['company']} | "
                     f"{r['niche'] or '—'} | {r['niche_source'] or '—'} | {r['cls']} | "
                     f"{r['attachment'] or '—'} | {r['note'] or 'ready'} |")
    needed = sorted({slug(r["niche"]) for r in blocked if r["cls"] == "industry" and r["niche"]})
    if needed:
        lines += ["", "## Lists to build before the next sweep", ""]
        lines += [f"- `lists/{n}.csv`" for n in needed]
    (batch / "REVIEW.md").write_text("\n".join(lines) + "\n")
    (batch / "batch.json").write_text(json.dumps(rows, indent=1))

    state["handled_reply_ids"] = sorted(set(state["handled_reply_ids"]) |
                                        {r["reply_id"] for r in rows})
    state["batches"].append({"batch": batch.name, "count": len(rows),
                             "ready": len(ready), "ask": len(ask), "blocked": len(blocked),
                             "created": datetime.now(timezone.utc).isoformat()})
    STATE.write_text(json.dumps(state, indent=1))

    print(f"Batch written: {batch}")
    print(f"  ready {len(ready)} | ask {len(ask)} | blocked {len(blocked)}")
    print("Nothing sent. Review REVIEW.md, then approve.")


if __name__ == "__main__":
    main()
