# Paste-into-Hermes prompt: build the metro local-business lists

Why these and not more industry lists: of the 64 interested leads as of
2026-10-08, 15 want an industry we already have a list for, 19 named a buying
signal no filter can express, 21 have no niche captured, and 8 asked for "local
businesses" or "small businesses" with no city on file. Those 8 are the only
group a new list can serve, and only once we know their metro.

---

Build one local-business contact list per US metro, so that when an agency owner
tells us which city their clients are in, we can attach the list in the same
minute instead of going away to build it.

## Output

One CSV per metro at `Leads/fulfillment/lists/<slug>.csv` in
`github.com/LGJ-Jonathan/Jay_Feldman`, named from the niche value exactly as the
copy uses it, lowercased with non-alphanumerics replaced by hyphens:
"Philadelphia businesses" becomes `philadelphia-businesses.csv`. That naming is
load-bearing: `scripts/fulfillment-sweep.py` finds a list by slugging the lead's
niche value, so a mismatch means the row shows as having no list.

Columns, in this order, matching the existing Google Maps sourced files exactly:

```
first_name,last_name,title,company,website,phone,city,state,email
```

Target 300 rows each. Below 150 rows, do not ship the file: the sender refuses a
thin list, and a thin list breaks the promise the copy makes.

## The metros

New York NY, Los Angeles CA, Chicago IL, Dallas TX, Houston TX, Washington DC,
Philadelphia PA, Miami FL, Atlanta GA, Boston MA, Phoenix AZ, San Francisco CA,
Seattle WA, Detroit MI, Minneapolis MN, San Diego CA, Tampa FL, Denver CO,
Baltimore MD, St. Louis MO, Orlando FL, Charlotte NC, San Antonio TX, Austin TX,
Portland OR, Sacramento CA, Pittsburgh PA, Las Vegas NV, Cincinnati OH,
Kansas City MO, Columbus OH, Indianapolis IN, Cleveland OH, San Jose CA,
Nashville TN, Jacksonville FL, Raleigh NC, Salt Lake City UT.

If you want to stage it, build these twelve first: New York, Los Angeles,
Chicago, Dallas, Houston, Philadelphia, Miami, Atlanta, Boston, Phoenix, Denver,
Tampa. They cover most of what agencies ask for.

## How to pull each one

Consulti local database, `POST https://www.consulti.ai/api/v1/local-leads/search`,
`Authorization: Bearer $CONSULTI_API_KEY`:

```json
{"keywords": ["Restaurant"], "cities": ["Philadelphia"], "states": ["PA"],
 "hasEmail": true, "page": 1, "size": 100}
```

- `states` takes **2-letter codes only**. Full state names silently return zero.
- Results come back under `businesses`, not `leads`. `has_more` is the pagination
  signal; `total` is not.
- Spread each metro across these categories so the list reads like a real
  cross-section of local business rather than 300 restaurants: Restaurant,
  Dentist, HVAC contractor, Plumber, Law firm, Real estate agency, Auto repair
  shop, Hair salon, Gym, Veterinarian, Roofing contractor, Landscaper, Medical
  clinic, Insurance agency, Accountant. Roughly 20 per category, then top up from
  whichever categories have depth in that metro.

Field mapping from a business record to the CSV: `owner_name` split into
`first_name` and `last_name`, `owner_title` to `title` (default "Owner" when
blank), `name` to `company`, then `website`, `phone`, `city`, `state`, `email`.

## Quality rules, each one learned the hard way

- **Drop any row with no `owner_name`.** The copy promises a name for each
  contact. Roughly half the local records have no owner, and shipping those
  breaks the promise.
- **Dedupe by email within a file, and across files.** Add every contact you
  keep to the Consulti audience list `lgj-give-first-fulfillment`
  (`POST /lists/{id}/add-leads`) so no contact is given to two different
  agencies. The local endpoint has no native exclusion, so also dedupe on
  `google_place_id` yourself.
- **Do not use the B2B database or its industry enum for this.** Measured:
  the `Automotive` industry filter returned tire manufacturers, auto auctions and
  General Motors, with 174 of 300 rows even auto-related, and `Law Practice`
  returned Perkins Coie and Akerman LLP. The Google Maps categories are precise
  and carry an owner name; the LinkedIn industry enum does not.
- **Do not build a national "small businesses" or "local businesses" list.**
  A generic national list is exactly what we are replacing. Ryan Blitz at
  Cerberus Digital Media rejected one in writing: "These seem like pre populated
  national lists. Not what we are looking for."
- Sanity-check each finished file by eye: 10 rows, and ask whether an agency
  selling to local businesses in that metro would be glad to receive it.

## When you are done

1. Run `python3 scripts/build-list-manifest.py`. It records each file's row
   count, domain count and columns into `scripts/list-manifest.json`, which is
   how the sweep knows a list exists, because the CSVs themselves are gitignored
   (prospect emails) and never reach a cloud checkout.
2. Commit and push `scripts/list-manifest.json` only. Never commit anything under
   `Leads/`.
3. Report a table: metro, rows, distinct domains, and anything you had to
   compromise on. Name every metro that came in under 150 rows and what the
   ceiling was, rather than padding it to look complete.

## Credits

About 300 per metro, so 11,400 for all 38 out of roughly 1.95M available. Check
`GET /api/v1/credits` before a big run.
