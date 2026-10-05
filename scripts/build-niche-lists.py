#!/usr/bin/env python3
"""
Builds one give-first CSV per industry niche from Consulti, for the fulfillment sweep
to attach. Run it again to refresh a niche; pass --only <slug> to rebuild just one.

Each contact is added to a single Consulti audience list which is then excluded from
later searches, so no contact appears in two niche files.

Usage:
  CONSULTI_API_KEY=capi_... python3 scripts/build-niche-lists.py [--only slug] [--size 300]
"""
import csv, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Leads" / "fulfillment" / "lists"
BASE = "https://www.consulti.ai/api/v1"
KEY = os.environ.get("CONSULTI_API_KEY", "")
AUDIENCE = "lgj-give-first-fulfillment"
PAGE_SIZE = 100

B2B_COLS = ["first_name", "last_name", "title", "company", "linkedin_url", "city", "state", "email"]
LOCAL_COLS = ["first_name", "last_name", "title", "company", "website", "phone", "city", "state", "email"]


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Authorization": "Bearer " + KEY,
                                          "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 * (attempt + 1)); continue
            print(f"    HTTP {e.code}: {e.read()[:200].decode('utf8','replace')}")
            return None
        except Exception as e:
            if attempt == 3:
                print(f"    {e}"); return None
            time.sleep(3 * (attempt + 1))
    return None


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def audience_id():
    d = call("GET", "/lists")
    for l in (d or {}).get("lists", []):
        if l.get("name") == AUDIENCE:
            return l["id"]
    d = call("POST", "/lists", {"name": AUDIENCE})
    return (d or {}).get("list", {}).get("id")


def split_name(full):
    parts = (full or "").strip().split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])


def pull_b2b(spec, target, exclude):
    rows, page = [], 1
    while len(rows) < target:
        body = {"countries": spec.get("countries", ["United States"]),
                "emailStatus": "good", "page": page, "size": PAGE_SIZE}
        for k in ("industries", "titles", "empMin", "empMax"):
            if k in spec:
                body[k] = spec[k]
        if exclude:
            body["excludeListId"] = exclude
        d = call("POST", "/leads/search", body)
        if not d or not d.get("leads"):
            break
        for L in d["leads"]:
            if not L.get("email"):
                continue
            rows.append({"first_name": L.get("first_name") or "", "last_name": L.get("last_name") or "",
                         "title": L.get("job_title") or "", "company": L.get("company_name") or "",
                         "linkedin_url": L.get("linkedin_url") or "", "city": L.get("city") or "",
                         "state": L.get("state") or "", "email": L["email"]})
        if not d.get("has_more"):
            break
        page += 1
    return rows[:target], B2B_COLS


def pull_local(spec, target, _exclude):
    rows, seen = [], set()
    for kw in spec.get("keywords", []):
        page, got = 1, 0
        per_kw = max(target // max(len(spec["keywords"]), 1), 20)
        while got < per_kw:
            d = call("POST", "/local-leads/search",
                     {"keywords": [kw], "hasEmail": True, "page": page, "size": PAGE_SIZE})
            if not d or not d.get("businesses"):
                break
            for b in d["businesses"]:
                em = b.get("email")
                if not em or em in seen:
                    continue
                if not (b.get("owner_name") or "").strip():
                    continue   # every contact needs a real name; the copy promises one
                seen.add(em)
                fn, ln = split_name(b.get("owner_name"))
                rows.append({"first_name": fn, "last_name": ln,
                             "title": b.get("owner_title") or "Owner",
                             "company": b.get("name") or "", "website": b.get("website") or "",
                             "phone": b.get("phone") or "", "city": b.get("city") or "",
                             "state": b.get("state") or "", "email": em})
                got += 1
            if not d.get("has_more"):
                break
            page += 1
    return rows[:target], LOCAL_COLS


def main():
    if not KEY:
        sys.exit("CONSULTI_API_KEY not set.")
    target = 300
    if "--size" in sys.argv:
        target = int(sys.argv[sys.argv.index("--size") + 1])
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None

    nmap = json.loads((ROOT / "consulti-niche-filter-map.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    aid = audience_id()
    print(f"audience list: {aid}")

    summary = []
    for niche, spec in nmap["industry"].items():
        s = slug(niche)
        if only and s != only:
            continue
        print(f"\n{niche}  ->  lists/{s}.csv")
        if spec["endpoint"] == "/local-leads/search":
            rows, cols = pull_local(spec, target, aid)
        else:
            rows, cols = pull_b2b(spec, target, aid)
        if not rows:
            print("    NOTHING RETURNED")
            summary.append((niche, 0, "empty")); continue

        path = OUT / f"{s}.csv"
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader(); w.writerows(rows)

        emails = [r["email"] for r in rows]
        if aid:
            call("POST", f"/lists/{aid}/add-leads", {"emails": emails})
        dom = len({e.split("@")[-1] for e in emails})
        print(f"    {len(rows)} rows, {dom} distinct domains")
        summary.append((niche, len(rows), f"{dom} domains"))

    print("\n=== SUMMARY ===")
    for n, c, note in summary:
        flag = "OK " if c >= 150 else "LOW"
        print(f"  {flag} {c:4}  {n}  ({note})")


if __name__ == "__main__":
    main()
