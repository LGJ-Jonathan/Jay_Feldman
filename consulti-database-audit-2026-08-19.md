# Consulti Database Services — Audit (2026-08-19)

Live API audit against `app.consulti.ai/api/v1` using key `capi_95b6…e877e`.
~2,000 records sampled, all 16 canonical filter sets pulled, every search endpoint probed.
Marketing pages (`consulti.ai/instagram-leads`, `/`, `/updates`) are behind a Vercel bot
checkpoint (403/429 to both curl and WebFetch), so every number below is measured from the
API, not from site copy.

**Account state:** 1,947,851 lead credits · 997,920 verification credits.

---

## 1. What Consulti actually sells now — five databases, not three

| DB | Endpoint | True size | Email coverage |
|---|---|---|---|
| B2B | `POST /leads/search` | uncountable (caps at 10001) | filterable, `emailStatus` enum |
| Local / Google Maps | `POST /local-leads/search` | uncountable | `hasEmail`, statuses `safe`/`risky` |
| Creators — podcast | `POST /creator-leads/search` `source:podcast` | **131,690** | **100%** |
| Creators — YouTube | `POST /creator-leads/search` `source:youtube` | **50,485** | **100%** |
| **Instagram (new)** | `POST /instagram/search` | uncountable, very large | **~3.4% raw** |

The Instagram DB is **undocumented in our `consulti-scrape` skill** and sits at
`/instagram/search`, *not* `/instagram-leads/search`. Anyone following the current runbook
cannot reach it.

**Creator total is 182,175 records.** The "847k+ creators" figure in our campaign copy only
holds if Instagram is counted in it. Podcasts + YouTube alone are ~182k.

### New since the last audit
- **`technologies` / `excludeTechnologies` on B2B** — 7,538 canonical values (Shopify, HubSpot,
  Klaviyo, 6sense…). Case-insensitive; off-list values return 0 cleanly. This is real
  technographic targeting and it is the single most sellable new capability.
- `local-states` expanded 58 → **128**: now accepts full state names *and* codes, and all
  Canadian provinces including MB/NL/NT/NU/PE/YT. Our skill doc saying "2-letter codes only"
  is stale.
- B2B `states` 877 → 942, `countries` 192 → 198.
- Per-database email-status enums, which do **not** match each other:
  B2B `bad/good/invalid/risky/unknown/valid` · Local `safe/risky` ·
  Podcast `catch_all/invalid/unknown/valid` · Instagram `bad/catch_all/good/risky`.
  A `emailStatus:"good"` that works on B2B and Instagram returns nothing on Local.

---

## 2. Hard platform ceilings (these govern list-building, not the DB size)

- **`total` caps at the literal `10001`.** Any slice bigger than that reports `10001`. You
  cannot size a segment from the API without narrowing until it drops below the cap.
- **Pagination skip cap: 100,000 rows.** `(page - 1) * size <= 100000`, enforced on *every*
  endpoint. **The maximum extractable from any single filter combination is 100k records.**
  A 500k-lead build needs ≥5 genuinely disjoint filter slices, planned up front.
- **Credits burn per record returned**, not per query (`credits_used == size`). Search results
  cache 30s server-side, so repeat queries in-window are free.
- **`excludeListId` is B2B-only.** Instagram has no native dedupe field at all — repeat
  Instagram pulls will re-serve the same records and re-charge for them. Dedupe must be
  client-side.

### Silent-filter money leak
`/leads/search` and `/instagram/search` **reject** unknown fields with a 400 and a list of
valid ones. `/local-leads/search` and `/creator-leads/search` **silently ignore** them and
return unfiltered results at full credit cost. A typo'd filter on Local or Creators looks
like a successful pull and quietly bills you for junk. Always smoke-test those two at
`size:1` and eyeball that the rows match the filter.

---

## 3. The Instagram database — measured

### Raw universe is mostly unusable
Random 800-record sample (sorted by username, 8 spread pages):

| | |
|---|---|
| Has email | **3.4%** |
| Has phone | 2.1% |
| Has website | 14.8% |
| Has category | 18.0% |
| Has country | 6.6% |
| Private accounts | 33.6% |
| Median followers | **225** |

This is a full Instagram crawl, not a lead list. The product is the ~3% that carries contact
data.

### The contactable slice is genuinely strong
500-record sample at `hasEmail:true`:

| | |
|---|---|
| Website present | 87.2% |
| Category present | 78.0% |
| Median followers | **652,963** |
| Status mix | good 35% · unverified 30% · risky 19% · catch_all 7% · bad 5% · unknown 3% |

At `hasEmail + emailStatus:"good"`: 94.4% have a website, 0% private, 47% are free-domain
(gmail/yahoo/icloud), 10% role accounts. Free-domain is normal and *correct* here — these are
creator inboxes, not company mailboxes.

**Verification is a one-off, not a rolling process.** All 740 "good" records I sampled carry
`email_verified_at` in **2026-07** — a single batch run last month. Nothing suggests
continuous re-verification, so freshness decays from that date.

### Real segment counts (slices small enough to escape the 10001 cap)

Instagram accounts → with email → with *verified good* email:

| Category (50k+ followers) | All | +email | +good | deliverable |
|---|---|---|---|---|
| Photographer | 6,052 | 3,403 | 1,158 | 19% |
| Fitness trainer | 3,740 | 2,000 | 806 | 22% |
| Advertising/marketing | 2,792 | 680 | 201 | **7%** |
| Restaurant | 2,110 | 1,294 | 391 | 19% |
| Real estate agent | 726 | 471 | 232 | 32% |
| Podcast | 701 | 346 | 185 | 26% |
| Beauty salon | 586 | 340 | 95 | 16% |
| E-commerce website | 482 | 325 | 98 | 20% |
| Business consultant | 406 | 184 | 50 | 12% |
| Lawyer & law firm | 317 | 179 | 66 | 21% |

Marketing accounts by follower floor, verified-good emails only:
**1k+ = 3,678 · 5k+ = 1,640 · 10k+ = 932 · 25k+ = 369 · 50k+ = 201 · 100k+ = 116.**

That is the honest ceiling of an Instagram-sourced marketing-agency list: **a few thousand
deliverable addresses, not tens of thousands.**

### Three defects worth knowing before anyone sells this

**1. Geo targeting is broken.** `GET /meta/instagram-countries` returns **zero values**, so
there is no canonical list. Behaviour:

| `countries` value | Result |
|---|---|
| `United States` | 79 |
| `USA` | 10001+ |
| `US` | 0 |
| `США` (Cyrillic) | 10001+ |

Country is populated on 6.6% of records overall (~40% of email-bearing ones) and stores mixed
Russian/English strings (`США`, `Индия`, `Кения`). **You cannot build a US-only Instagram list
through the country filter.** Any "local Instagram leads" pitch is unsupported today.

**2. Category ≠ industry.** Instagram's self-declared `Advertising/marketing` label means
"this account posts promos." At 250k+ followers that segment is shoutout and repost pages
(`@blackinkcrews`, `@the.world.beauty.universe__`), not agencies. It only becomes real
agencies in the 5k–50k band — and there it is heavily non-English (Turkish, Korean, Hindi,
Arabic, Azeri), with no working geo filter to strip that out. Categories are also fragmented
across 250 near-duplicate values: `Advertising/marketing`, `Advertising agency`, `Marketing
agency`, `Social media agency`, `Media agency`, `Internet marketing service` are six separate
buckets you must union manually.

**3. Casing is strict and unforgiving** — but it fails loudly, which is good.
`Gym/physical fitness center` → 400; the canonical value is `Gym/Physical fitness center`.
`Dentist` → 400; canonical are `Dentist & dental office`, `General dentist`, `Cosmetic dentist`.

### The actual differentiator: `bioKeywords`
No other Consulti database has free-text bio search, and it outperforms the category filter
for intent targeting. Real counts (5k+ followers, verified-good email):

| Bio keyword | Accounts |
|---|---|
| `link in bio` | 2,117 |
| `we help` | 1,820 |
| `dm for collab` | 1,440 |
| `book a call` | 619 |
| `agency owner` | 180 |

Spot-checking `agency owner` returns actual agency owners with business-domain emails —
qualitatively cleaner than the `Advertising/marketing` category at the same follower floor.
Paired with `excludeKeywords` and `excludeAdultContent`, this is the way to build an
Instagram list. Instagram is also the only DB with `sortBy` (`followers|posts|engagement|username`).

---

## 4. Positioning read

**The Instagram database is a creator-sourcing tool, not a B2B lead database.** Its
email-bearing population has a median of ~650k followers, 47% gmail addresses, and website +
bio + engagement data. That profile serves a brand hunting influencers or UGC partners
extremely well. It serves an agency buying a cold-email list poorly — the deliverable volumes
are in the hundreds-to-low-thousands per niche, and there is no working country filter.

Concretely:

- **Sell Instagram to brands/DTC for influencer and UGC outreach.** Lead with `bioKeywords` +
  follower band + engagement sort. That is a capability Apollo, Instantly, and Clay do not have.
- **Do not sell Instagram as a source of local-business or agency lead lists.** Geo is broken
  and the agency segment tops out around 1,640 deliverable addresses at 5k+ followers.
- **The sharper new story for existing B2B buyers is `technologies`** — 7,538 technographic
  filters landed in July and are not in any of our copy. "Everyone running Shopify + Klaviyo
  in Florida" is a stronger, more defensible pitch than another Instagram angle.
- **Fix the claim math in campaign copy.** Podcasts + YouTube = 182,175. Only count Instagram
  toward "847k+ creators" if we are willing to have that number checked.
- **Re-verification is the credible data-quality hook** we still are not using. Instagram
  emails were verified once in July 2026. A rolling re-verification commitment would be a real
  differentiator; claiming freshness without one would not survive scrutiny.

## 5. Skill maintenance required

`~/.claude/skills/consulti-scrape/SKILL.md` is out of date on five points:
1. No Instagram database documented — add `POST /instagram/search` and its 20-field schema.
2. No `technologies` / `excludeTechnologies` on the B2B schema.
3. "Pagination cap 10001" is wrong — the operative limit is the **100,000-row skip cap**.
4. `local-states` is 128 values (codes *and* full names, all Canadian provinces), not 58 codes.
5. Email-status enums are per-database and mutually incompatible; the doc lists only the B2B set.
