# Give-First list fulfillment — build spec

Delivering the promised contact list to agency owners who reply interested, without a human
assembling it by hand, and without a second system that can email a prospect.

Owner of the runtime: whoever holds Bob. Requested by Shara (shara@leadgenjay.com).
Status: spec. Nothing below is built yet.

---

## The one rule this must not break

**A prospect must never receive two reply emails from us.** Hermes on Bob is the only runtime
allowed to send to a prospect. This spec therefore adds a *path inside Hermes*. It does not add
an n8n flow, a cron script, or anything on Shara's own machine that sends mail. See
`cold-email-reply-agent` skill, Pathway A.

## The gate: campaign allowlist

Fulfillment fires **only** when the Bison reply's `campaign_id` is on this list. Hard-coded in
the filter, checked before the model is ever asked anything.

| Campaign id | Name | Niche variable |
|---|---|---|
| 1298 | Blitz Agencies - Give-First 2 (9/26) Shara - Optimized | `signal_topic` |
| 1313 | Clutch Agencies - (coworker-9/26) Shara - Optimized | `niche` |
| 1315 | Clutch Agencies - (9/26) Shara - Optimized | `niche` |
| 1145 | Consulti Agencies - Give-First (8/22) Shara - optimizations | none |

Why a campaign allowlist and not a tag:

- There is **no tag named "Shara"** in the Consulti workspace. The tags that exist are Interested,
  Meeting Booked, Hard No, Soft No, Auto Reply, Follow up 7d, Follow up 30d, Booked, Lead Magnet,
  plus the provider tags.
- **Bison's `tag_ids` filter on `/leads` is silently ignored.** Verified 2026-10-05: `tag_ids[]=959`,
  `tag_ids=959`, `tag_ids[]=777` and `tags[]=959` all return the same unfiltered 76,262 leads, and
  the first row carries only the `Google` tag. A gate built on it would have passed everything.
- Tags live on the **lead**, which is workspace-global. A lead in two campaigns carries the tag in
  both, so a tag cannot express "this campaign's leads".
- `campaign_id` is already on the reply payload. No extra call, nothing to remember at upload time.

Add a `Lead Magnet` tag attach after a successful send as a record, not as a gate.

## Where the niche comes from

Tags are not on the reply webhook's nested `lead` object. `GET /api/leads/{id}` **does** return
both `tags[]` and `custom_variables[]`, so the lane makes that one call and reads the niche with a
fallback chain:

```
signal_topic  →  niche  →  industry  →  client_niche  →  (none: ask)
```

Measured on the 56 interested leads that have a lead record: `signal_topic` 10, `niche` 28,
`industry` 2, nothing at all 16. The 16 are all campaign 1145, which never used a niche variable.

## The lane

```
Bison lead_replied → existing Hermes route (hermes-hooks.nextwave.io → Bob → :8644)
  → bison-reply-filter.py
      ├ existing: dedupe by reply id, killswitch, automated-reply drop, workspace map
      └ NEW: campaign_id in allowlist? else fall through to normal reply handling
  → Hermes turn, skill cold-email-reply-agent, intent give_first_fulfillment
  → GET /api/leads/{id}          read custom_variables + tags
  → resolve niche via the chain, then classify against consulti-niche-filter-map.json
  → industry class: attach the pre-built CSV
    geo class:      build per-lead from /local-leads/search in their metro
    intent class:   no list, send the one-question reply
    no niche:       no list, send the one-question reply
  → POST /api/replies/{id}/reply with the CSV attached   (endpoint supports attachments)
  → PATCH /api/replies/{id}/mark-as-interested  +  attach Lead Magnet tag
  → append to fulfilled.log: reply id, lead id, niche, class, row count, file, NEW reply id
```

The returned `data.reply.id` is the only proof a send happened. Never retry the send POST — it is
non-idempotent and a retry re-mails the prospect.

## Build the lists ahead of time, do not generate them live

The industry-class niches are a closed set. Pull each one once, eyeball it once, store it as
`{niche-slug}.csv` on Bob. Fulfillment then = pick file, attach, reply. No API latency inside the
reply, no credit surprise, and no chance a search returning 11 rows goes out as "300 contacts".

CSV columns, exactly what Email 2 promises and nothing else:

```
first_name, last_name, title, company, linkedin_url, city, email
```

Live `/leads/search` stays as the fallback for a niche with no cached file.

## What the niche data actually looks like

The 40 resolvable niches on interested leads split three ways, and only the first can be
auto-fulfilled. Full mapping in `consulti-niche-filter-map.json`.

| Class | Count | Niches | Handling |
|---|---|---|---|
| **Industry** | 16 | auto dealerships (3), law firms (2), marketing & advertising (2), ecommerce brands, healthcare, nonprofits, manufacturing, home services, financial services, energy, media & entertainment, cannabis brands | Pre-built CSV, auto-send |
| **Geo / generic** | 8 | small businesses (3), local businesses (3), SMBs, B2B businesses | Built per-lead in their metro |
| **Intent, not industry** | 13 | planning a website redesign (3), planning a rebrand (3), investing in digital marketing (3), producing video content (2), needing creative support (2), investing in SEO, ecommerce marketing, fractional CMO | **Cannot be fulfilled.** Ask one question |
| **No niche on file** | 16 | all campaign 1145 | **Cannot be fulfilled.** Ask one question |

**The intent class is the thing to decide before building anything.** The Clutch campaigns enriched
`niche` with buying signals rather than industries, so "companies planning a rebrand" has no
Consulti filter behind it and never will. 29 of the 56 interested leads (13 intent + 16 no niche)
land here. For them the correct reply is not a list, it is:

> Happy to pull it. What kind of businesses do you want them to be?

Their answer then routes through the industry map on the next turn. That is still automated, it
just takes one extra round trip, and it is the difference between a useful file and a file that
gets us remembered as the people who sent a random list.

## Guardrails

Inherited from the existing lane, unchanged: one send per reply id ever, 50 sends/day/workspace,
2 sends/day/lead, live re-fetch before send so a reply that turned out to be `automated_reply` is
refused, body ≤1500 chars, no unrendered `{merge}` tokens.

Added for this path:

- **Attach, never link.** The lane's interlock allows links only to consulti.ai, and a file in the
  thread beats a link anyway. `POST /api/replies/{id}/reply` supports attachments.
- **Row-count floor.** Refuse to send a file under 150 rows. A thin list breaks the promise.
- **Human gate for the first 20.** Run under `~/.hermes/reply-agent.dryrun` so the lane assembles
  the CSV and drafts the reply but cannot send. Review 20 real niche matches, then go live. The
  risk here is not a broken script, it is a confidently wrong niche, and only eyes catch that.

## Backlog waiting on this

58 interested replies across the four campaigns as of 2026-10-05, all still in Inbox: 1145 → 22,
1315 → 16, 1298 → 12, 1313 → 8. Of these, 16 are auto-fulfillable from a pre-built industry file
today, 8 need a per-lead geo build, and the rest need the clarifying question.

## Open items

1. **Bob access.** Edits go to the canonical copies in lgj-os and push with `scripts/bob/bob-push.sh`,
   never to Bob directly. Shara has neither the repo nor ssh, so this change needs the Bob owner.
2. **Webhook `195 LGJ magnet fulfillment`** already exists in Bison carrying a `?token=`. Find out
   what it points at before building — a lane may be half-built already.
3. **Consulti API key, Pro plan, credit balance.** Pre-building the 12 industry files at 300 rows is
   ~3,600 lead credits, one time. Live-per-reply is 300 every time, forever.
4. **Fix the Clutch enrichment** so `niche` carries an industry, not a buying signal. Otherwise every
   future Clutch campaign reproduces the intent-class problem at scale.
