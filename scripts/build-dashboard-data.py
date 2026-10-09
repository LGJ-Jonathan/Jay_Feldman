#!/usr/bin/env python3
"""
Regenerates dashboard/data.json, the only thing the hosted desk reads.

Run it as often as you like. It talks to Bison for campaign counters, reads the
batches the sweep wrote, the staged reply bodies, the list manifest and the send
log, and writes one JSON file. It sends nothing and decides nothing.

  BISON_API_KEY=... python3 scripts/build-dashboard-data.py

The file it writes carries prospect names and email addresses, so whatever
serves it must not be open to the internet. See dashboard/README.md.
"""
import json, os, re, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "data.json"
BASE = "https://send.leadgenjay.com/api"
KEY = os.environ.get("BISON_API_KEY", "")

CAMPAIGNS = {
    1145: ("Consulti Agencies - Give-First", "500, and 50 local owners", "none, must ask"),
    1315: ("Clutch Agencies", "500, and ~300 on the alt step", "NICHE"),
    1313: ("Clutch Agencies - coworker", "300", "NICHE"),
    1298: ("Blitz Agencies - Give-First 2", "500, and 300 on the alt step", "SIGNAL_TOPIC"),
}
B2B = {"ecommerce-brands", "energy-companies", "financial-services-firms",
       "manufacturing-companies", "marketing---advertising",
       "media-and-entertainment-companies", "nonprofits",
       "coaches-speakers-and-sales-consultants"}


def get(path, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                print(f"  bison {path} failed: {e}", file=sys.stderr)
                return None


def load(p, default):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return default


def main():
    stale = []

    campaigns = []
    for cid, (short, promised, var) in CAMPAIGNS.items():
        d = get(f"/campaigns/{cid}")
        c = (d or {}).get("data") or {}
        if not c:
            stale.append(f"campaign {cid} counters could not be refreshed")
        sent = c.get("emails_sent") or 0
        campaigns.append({
            "id": cid, "name": short, "full_name": c.get("name") or short,
            "status": c.get("status") or "unknown", "sent": sent,
            "replies": c.get("unique_replies") or 0, "interested": c.get("interested") or 0,
            "bounced": c.get("bounced") or 0, "unsub": c.get("unsubscribed") or 0,
            "reply_rate": round((c.get("unique_replies") or 0) / sent * 100, 2) if sent else 0,
            "promised": promised, "niche_var": var,
        })

    lists = []
    for f, m in sorted(load(ROOT / "scripts/list-manifest.json", {"lists": {}})["lists"].items()):
        slug = f[:-4]
        lists.append({"slug": slug, "rows": m["rows"], "domains": m["domains"],
                      "has_linkedin": slug in B2B,
                      "source": "B2B database" if slug in B2B else "Google Maps local",
                      "ok": m["rows"] >= 150})

    leads = {}
    for p in sorted((ROOT / "Leads/fulfillment").glob("batch-*/batch.json")):
        for r in json.load(open(p)):
            leads[r["reply_id"]] = r

    plan = load(ROOT / "Leads/fulfillment/staged/send-plan.json",
                {"ready": [], "held_for_you": {}, "attachments": {}})
    sent_ids = {str(r.get("reply_id")) for r in load(ROOT / "scripts/sent-log.json", {"sent": []})["sent"]}
    staged_dir = ROOT / "Leads/fulfillment/staged"

    staged = []
    for rid in plan["ready"]:
        r = leads.get(rid)
        if not r:
            continue
        body = staged_dir / f"{rid}.txt"
        staged.append({
            "id": rid, "name": r["first_name"], "company": r["company"], "email": r["email"],
            "campaign": r["campaign"][:34], "received": r["received"][:10],
            "attachment": plan["attachments"].get(str(rid)) or "",
            "lane": "sent" if str(rid) in sent_ids else "ready",
            "body": body.read_text().strip() if body.exists() else "",
            "reply": (r.get("reply_text") or "").strip()[:500],
        })
    for rid, why in plan["held_for_you"].items():
        r = leads.get(int(rid))
        if not r:
            continue
        staged.append({
            "id": int(rid), "name": r["first_name"], "company": r["company"], "email": r["email"],
            "campaign": r["campaign"][:34], "received": r["received"][:10], "attachment": "",
            "lane": "held", "why": why, "body": "",
            "reply": (r.get("reply_text") or "").strip()[:500],
        })

    answered = [{"id": r["reply_id"], "name": r["first_name"], "company": r["company"],
                 "email": r["email"], "campaign": r["campaign"][:34],
                 "pushback": bool(r.get("lead_pushed_back")),
                 "reply": (r.get("reply_text") or "").strip()[:300]}
                for r in leads.values() if r.get("answered")]

    demand = load(ROOT / "scripts/list-demand.json", {})
    codes = load(ROOT / "scripts/gift-codes.json", {"codes": []})["codes"]

    payload = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stale": stale,
        "sender_armed": not (ROOT / "scripts/sender.off").exists(),
        "campaigns": campaigns, "lists": lists, "staged": staged, "answered": answered,
        "gift_codes": {"unused": sum(1 for c in codes if not c.get("used")),
                       "total": len(codes)},
        "totals": {
            "sent": sum(c["sent"] for c in campaigns),
            "replies": sum(c["replies"] for c in campaigns),
            "interested": len(leads),
            "list_rows": sum(l["rows"] for l in lists), "lists": len(lists),
            "ready": sum(1 for s in staged if s["lane"] == "ready"),
            "held": sum(1 for s in staged if s["lane"] == "held"),
            "sent_replies": sum(1 for s in staged if s["lane"] == "sent"),
            "answered": len(answered),
            "demand_human": len(demand.get("human", [])),
            "demand_ask": len(demand.get("ask", [])),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=1))
    tmp.replace(OUT)          # atomic, so a fetch never reads half a file
    t = payload["totals"]
    print(f"{OUT.relative_to(ROOT)}: {t['ready']} ready, {t['held']} held, "
          f"{t['sent_replies']} sent, {t['answered']} answered by the bot, {t['lists']} lists")
    if stale:
        print("  stale:", "; ".join(stale))


if __name__ == "__main__":
    main()
