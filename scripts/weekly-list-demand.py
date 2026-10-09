#!/usr/bin/env python3
"""
Weekly list-demand report for the give-first lane.

Answers three questions, in order of how much they cost to get wrong:

  1. Which leads can be sent a list right now?
  2. Which lists do we need to build, and with what Consulti filters?
  3. Which leads must a human read, because no rule should answer them?

It reads the batches the sweep already wrote. It sends nothing, builds
nothing and writes no prospect-facing text. Output is a digest plus
scripts/list-demand.json for the builder to consume.

The part that earns its keep is read_reply(): the sweep resolves a niche
from the campaign's merge variables, which on a real batch left 37 of 62
leads looking like "ask them what niche". Reading the reply body instead
found that a third of those had already said what they wanted, and that
several were not list requests at all.

Usage:
  python3 scripts/weekly-list-demand.py            # last 7 days
  python3 scripts/weekly-list-demand.py --days 30
  python3 scripts/weekly-list-demand.py --all
"""
import csv, glob, json, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTS = ROOT / "Leads" / "fulfillment" / "lists"
MAP = ROOT / "consulti-niche-filter-map.json"
MANIFEST = ROOT / "scripts" / "list-manifest.json"
SENT_LOG = ROOT / "scripts" / "sent-log.json"
OUT = ROOT / "scripts" / "list-demand.json"
MIN_ROWS = 150

# A reply whose first sentence is just a yes. Signatures, "thanks" and
# pleasantries follow most of them, so the test is on the opening clause,
# not the whole paragraph.
AFFIRMATIVE = re.compile(
    r"^\W*(yes|yep|yeah|sure|ok|okay|please|pls|sounds good|go ahead|send|send it|"
    r"send them|send over|send me|please send|please do|i'?m interested|interested|"
    r"certainly|absolutely|of course|sure thing|yes please|let'?s see|would love)\b", re.I)

# Signature and quoted-thread markers. Everything after the first hit is noise.
# Explicit markers only. An earlier version also treated any "Name Surname" at
# the start of a line as a signature, which ate entire replies: Carl's whole
# brief and Phillip's "i'm confused why i would want this list?" both reduced
# to an empty string, and both were then classified from the campaign variable.
SIG = re.compile(r"\n\s*(thanks\b|thank you|best regards|best,|regards|cheers|respectfully|"
                 r"godspeed|sincerely|--|__|sent (via|from)|get outlook|"
                 r"on .{0,200}?wrote:|on \d{1,2}/\d{1,2}/\d{2,4}|from:\s|"
                 r"notice:|disclaimer|confidential|this electronic message|"
                 r"\d{3}[-.) ]\d{3}[-.]\d{4})", re.I)
GREETING = re.compile(r"^\s*(hi|hey|hello|dear|good (morning|afternoon))\b[^\n]{0,40}\n+", re.I)
# URLs carry query strings, and a "?" in a tracking link is not a question.
# Ron Kohl's signature link alone was enough to route him to a human.
URL = re.compile(r"<?https?://\S+>?|<[^>\s]+@[^>\s]+>|\[(image|cid)[^\]]*\]", re.I)

# Someone selling TO us, not asking for a list.
PITCH = re.compile(r"looking to bring on|we'?re hiring|i can help you|our team handles|"
                   r"we speciali[sz]e in helping|offer our services|partner with you|"
                   r"white ?label|pay a commission|do not pay for", re.I)
# Wants a meeting rather than a file.
CALL = re.compile(r"booking link|calendly|hs-sales-engage|schedule a (call|time)|"
                  r"grab (a )?time|jump on a call|hop on a call|meet with .{0,20}from", re.I)
# Housekeeping that must not be answered with a list.
ADMIN = re.compile(r"(update|change|use)\b[^.]{0,40}\bemail|unsubscribe|remove me|"
                   r"take me off|no longer (with|at)|has left", re.I)
# Wants terms, provenance or a deck before anything else.
QUESTION = re.compile(r"how much|what.{0,12}cost|for free|pricing|\bprice\b|exclusive|"
                      r"where do you get|what.{0,12}(source|sources)|lead source|methodology|"
                      r"intent|business deck|key services|is this (a )?different|"
                      r"than i'?d find|what are you offering|what you are offering|"
                      r"not.{0,12}sure what|share more|tell me more|more about", re.I)
# They want something other than the 300 on offer.
# They want something other than what was offered: a different size, a revenue
# floor, or a company tier. An earlier version required four digits after the
# "$", so "above $500k in monthly revenue" slipped through and Jeremy was
# staged a list explicitly capped at 500 employees.
MISMATCH = re.compile(r"much larger|larger list|bigger list|more than \d|only need|instead of|"
                      r"rather than|list of \d{3,}|\d{3,}\s*(of those|contacts|leads)|"
                      r"\$\s?[\d.,]+\s?[kmb]\b|\$[\d.,]{3,}|"
                      r"\b\d[\d.,]*\s?(k|m|mm|million|billion)\b|"
                      r"\benterprise\b|\bmid-?market\b|upwards of|at least \$?[\d,]|"
                      r"\b(annual|monthly) revenue\b|\bper (year|month)\b", re.I)

GEO = re.compile(r"\b(in|near|around|within)\b[^.]{0,60}\b(city|cities|state|states|county|"
                 r"metro|area|miles|zip)\b|\b[A-Z][a-z]+,\s?[A-Z]{2}\b", re.I)

# Words a lead uses -> the niche key in consulti-niche-filter-map.json.
SYNONYMS = {
    "law firms": ["law firm", "lawyer", "attorney", "legal practice", "personal injury"],
    "auto dealerships": ["dealership", "car dealer", "auto dealer", "automotive dealer"],
    "healthcare companies": ["healthcare", "medical practice", "dental", "dentist", "clinic",
                             "chiropract", "med spa", "physical therap"],
    "home service companies": ["home service", "hvac", "plumber", "plumbing", "roofer",
                               "roofing", "electrician", "landscap", "contractor"],
    "cannabis brands": ["cannabis", "dispensar", "cbd", "hemp", "marijuana"],
    "ecommerce brands": ["ecommerce", "e-commerce", "dtc", "online store", "shopify"],
    "manufacturing companies": ["manufactur", "industrial", "machin", "fabricat"],
    "financial services firms": ["financial services", "financial advisor", "wealth",
                                 "accounting", "cpa", "insurance", "mortgage"],
    "energy companies": ["energy", "solar", "oil and gas", "renewable"],
    "media and entertainment companies": ["media", "entertainment", "film", "production company",
                                          "broadcast", "podcast"],
    "nonprofits": ["nonprofit", "non-profit", "charity", "ngo", "foundation"],
    "marketing & advertising": ["marketing agenc", "ad agenc", "advertising agenc"],
    "coaches speakers and sales consultants": ["coach", "speaker", "sales consultant",
                                               "consultant"],
    "restaurants and local food": ["restaurant", "cafe", "coffee", "bar", "brewery", "food truck"],
    "fitness and gyms": ["gym", "fitness", "crossfit", "yoga studio", "pilates"],
    "real estate": ["real estate", "realtor", "broker", "property manage"],
    "construction": ["construction", "builder", "remodel", "general contractor"],
}


def load(path, default):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return default


def list_rows(slug):
    """Row count for a built list, from the CSV locally or the manifest in the cloud."""
    p = LISTS / f"{slug}.csv"
    if p.exists():
        with open(p) as f:
            return max(sum(1 for _ in f) - 1, 0)
    entry = load(MANIFEST, {}).get("lists", {}).get(f"{slug}.csv")
    return entry.get("rows", 0) if entry else 0


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def read_reply(text, variable_niche, intent_niches=()):
    """Classify a lead from what they actually wrote.

    Returns (lane, niche, why). The campaign's merge variable is trusted only
    when the reply adds nothing, because that variable describes the campaign's
    guess at the lead, not the lead's answer. An intent-flavoured variable
    ("companies planning a rebrand") is never trusted, because no Consulti
    filter expresses it.
    """
    body = (text or "").strip()
    if not body:
        return "human", None, "empty reply body"
    # Cut the signature and the quoted thread. What remains is what they wrote.
    # Outlook prefixes quoted threads with a BOM, which is not whitespace, so
    # the signature cut missed it and Carla's quoted thread was read as hers.
    body = body.replace("\ufeff", "").replace("\u200b", "").replace("\xa0", " ")
    body = GREETING.sub("", body)
    m = SIG.search("\n" + body)
    said = ("\n" + body)[:m.start() if m else 800].strip()
    if not said:
        said = body[:400]
    said = URL.sub(" ", said).strip()
    low = said.lower()

    if ADMIN.search(said):
        return "human", None, "housekeeping: do not answer this with a list"
    if PITCH.search(said):
        return "human", None, "they are selling to us, not asking for a list"
    if CALL.search(said):
        return "human", None, "wants a call or sent a booking link"
    if MISMATCH.search(said):
        return "human", None, "wants a different size or shape of list than we offered"
    if QUESTION.search(said) or "?" in said:
        return "human", None, "asked a question, so answer it before sending anything"

    hits = [niche for niche, words in SYNONYMS.items() if any(w in low for w in words)]
    if len(hits) > 1:
        return "human", None, f"named several niches: {', '.join(hits)}"
    if len(hits) == 1:
        geo = " and named a place" if GEO.search(said) else ""
        return "named", hits[0], f"named their niche in the reply{geo}"
    if GEO.search(said) and not AFFIRMATIVE.match(said):
        return "human", None, "named a place but no industry we recognise"

    if AFFIRMATIVE.match(said):
        if variable_niche and variable_niche.lower() in intent_niches:
            return "ask", None, (f"plain yes, and the campaign variable "
                                 f"('{variable_niche}') is an intent phrase no filter expresses")
        if variable_niche:
            return "variable", variable_niche, "plain yes, niche from the campaign variable"
        return "ask", None, "plain yes, no niche anywhere"

    return "human", None, "reply says something a rule should not answer"


def main():
    days = 7
    if "--all" in sys.argv:
        days = 10_000
    elif "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    sent = {str(r.get("reply_id")) for r in load(SENT_LOG, {"sent": []})["sent"]}
    nmap = load(MAP, {"industry": {}})
    intent_niches = {k.lower() for k in nmap.get("intent", {}) if not k.startswith("_")}

    leads = {}
    for p in sorted(glob.glob(str(ROOT / "Leads/fulfillment/batch-*/batch.json"))):
        for r in json.load(open(p)):
            leads[r["reply_id"]] = r

    ready, build, ask, human, skipped = [], [], [], [], []
    demand = {}
    for r in sorted(leads.values(), key=lambda x: x["received"]):
        rid = r["reply_id"]
        if datetime.fromisoformat(r["received"].replace("Z", "+00:00")) < cutoff:
            continue
        if str(rid) in sent:
            skipped.append((rid, "already sent")); continue
        if r.get("answered"):
            skipped.append((rid, "another system answered the thread first")); continue

        lane, niche, why = read_reply(r.get("reply_text"), r.get("niche"), intent_niches)
        row = {"reply_id": rid, "name": r.get("first_name"), "company": r.get("company"),
               "email": r.get("email"), "campaign": r.get("campaign"),
               "received": r["received"][:10], "niche": niche, "why": why,
               "reply": (r.get("reply_text") or "").strip()[:160].replace("\n", " ")}

        if lane == "human":
            human.append(row); continue
        if lane == "ask":
            ask.append(row); continue

        s = slug(niche)
        rows = list_rows(s)
        row["list"] = f"{s}.csv"
        row["rows"] = rows
        if rows >= MIN_ROWS:
            ready.append(row)
        else:
            build.append(row)
            d = demand.setdefault(niche, {"niche": niche, "slug": s, "rows_today": rows,
                                          "leads": [], "spec": nmap["industry"].get(niche)})
            d["leads"].append({"reply_id": rid, "name": row["name"], "company": row["company"]})

    w = sys.stdout.write
    w(f"\nGIVE-FIRST LIST DEMAND  last {days} days\n")
    w(f"{'='*72}\n")
    w(f"  {len(ready):3}  ready to send, list already built\n")
    w(f"  {len(build):3}  waiting on a list build\n")
    w(f"  {len(ask):3}  plain yes with no niche, needs the question asked\n")
    w(f"  {len(human):3}  must be read by a human\n")
    w(f"  {len(skipped):3}  skipped (sent already, or answered by another system)\n")

    if ready:
        w(f"\n{'-'*72}\nREADY TO SEND\n")
        for r in ready:
            w(f"  {r['name'][:14]:15} {r['company'][:26]:27} {r['list'][:34]:35} {r['rows']:>4} rows\n")

    if build:
        w(f"\n{'-'*72}\nBUILD THESE LISTS\n")
        for d in sorted(demand.values(), key=lambda x: -len(x["leads"])):
            who = ", ".join(f"{l['name']} at {l['company']}" for l in d["leads"])
            w(f"\n  {d['niche']}  ({len(d['leads'])} lead{'s' if len(d['leads']) != 1 else ''}: {who})\n")
            w(f"    today: {d['rows_today']} rows, need {MIN_ROWS}\n")
            if d["spec"]:
                w(f"    run:   python3 scripts/build-niche-lists.py --only {d['slug']} --size 300\n")
            else:
                w(f"    no spec in consulti-niche-filter-map.json yet. Add one under\n")
                w(f"           industry[\"{d['niche']}\"] before building.\n")

    if ask:
        w(f"\n{'-'*72}\nASK WHICH NICHE  (plain yes, nothing to go on)\n")
        for r in ask:
            w(f"  {r['name'][:14]:15} {r['company'][:30]:31} {r['reply'][:34]}\n")

    if human:
        w(f"\n{'-'*72}\nREAD THESE YOURSELF\n")
        for r in human:
            w(f"\n  {r['name']} at {r['company']}  <{r['email']}>  reply {r['reply_id']}\n")
            w(f"    why:  {r['why']}\n")
            w(f"    said: {r['reply'][:120]}\n")

    OUT.write_text(json.dumps(
        {"generated": datetime.now(timezone.utc).isoformat(), "window_days": days,
         "ready": ready, "build": build, "ask": ask, "human": human,
         "demand": list(demand.values())}, indent=1) + "\n")
    w(f"\n{'='*72}\nwrote {OUT.relative_to(ROOT)}\n\n")


if __name__ == "__main__":
    main()
