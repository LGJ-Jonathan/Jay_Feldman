#!/usr/bin/env python3
"""
Records what is on the list shelf, without the prospect data.

The CSVs hold prospect emails and are gitignored, so a cloud run of the sweep
cannot see them. This manifest carries only the row count, domain count and
column names, which is all the sweep needs to decide a niche is fulfillable.
Re-run it after building or refreshing any list.
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTS = ROOT / "Leads" / "fulfillment" / "lists"
OUT = ROOT / "scripts" / "list-manifest.json"

m = {}
for p in sorted(LISTS.glob("*.csv")):
    rows = list(csv.DictReader(open(p)))
    if not rows:
        continue
    m[p.name] = {"rows": len(rows),
                 "domains": len({r["email"].split("@")[-1] for r in rows if r.get("email")}),
                 "columns": list(rows[0].keys())}
OUT.write_text(json.dumps({"lists": m}, indent=1) + "\n")
print(f"{len(m)} lists recorded in {OUT.relative_to(ROOT)}")
for k, v in m.items():
    print(f"  {v['rows']:4}  {k}")
