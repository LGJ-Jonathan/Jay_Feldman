# Give-First fulfillment in n8n

Three workflows, not one. The split is deliberate: **nothing that prepares a reply
is allowed to send it.** Preparation runs on a timer, sending runs only from your
approval click, and the shelf refills itself overnight.

| Workflow | Trigger | What it does | Can it email a prospect? |
|---|---|---|---|
| WF-1 Detect & Prepare | Schedule, every 15 min | Finds new interested replies, resolves the niche, mints a list link, writes a draft | **No** |
| WF-2 Approve & Send | Webhook from your Approve button | Re-runs the guards, sends the one reply | Yes, once per reply id |
| WF-3 Shelf top-up | Schedule, nightly | Rebuilds any list under 300 rows from Consulti | **No** |

---

## 0. Before you build

### Credentials (n8n → Credentials, type **Header Auth**)

| Name | Header | Value |
|---|---|---|
| `Bison Consulti WS` | `Authorization` | `Bearer 586\|wBRgtr7afy1bUa0tnnlDBL8bkuZJUshVY1by7cMC11d1f843` |
| `Consulti API` | `Authorization` | `Bearer capi_...` |
| `List Server` | `X-Mint-Key` | whatever you set as `MINT_KEY` on the server |

Store the Bison key as a **credential**, never as an env var in an expression. The
key contains a `|`. In a shell that pipes and silently empties the key; we lost a
whole batch to a 401 that way.

### Data store

Postgres if you have it, n8n Data Tables if you don't. Four tables:

```sql
-- every reply we have ever looked at, so we never look twice
seen        (reply_id BIGINT PRIMARY KEY, first_seen TIMESTAMPTZ)

-- the approval queue, one row per prepared reply
queue       (reply_id BIGINT PRIMARY KEY, campaign_id INT, lead_id BIGINT,
             email TEXT, first_name TEXT, company TEXT, niche TEXT,
             outcome TEXT,          -- ready | ask | hold | build
             list_file TEXT, rows INT, link TEXT, body TEXT, note TEXT,
             status TEXT,           -- pending | sent | held | error
             prepared TIMESTAMPTZ, decided TIMESTAMPTZ)

-- the send ledger. One row here means one email left the building.
sent_log    (reply_id BIGINT PRIMARY KEY, new_reply_id BIGINT, to_email TEXT,
             link TEXT, sent_at TIMESTAMPTZ)

-- mailbox map, refreshed by WF-3
mailboxes   (email TEXT PRIMARY KEY, sender_email_id INT)
```

`sent_log` is the one that matters. It is keyed on `reply_id`, so the
database itself refuses a second send to the same thread even if every other
guard fails.

### One code change on the list server

n8n needs to mint links over HTTP rather than by CLI. I added `POST /api/mint` to
`scripts/dashboard-server.py` for exactly this. It takes
`{"reply_id","list","email","rows"}` with an `X-Mint-Key` header and returns
`{"url": "..."}`, idempotent per reply+list like the CLI version.

---

## WF-1 — Detect & Prepare (every 15 minutes)

**1. Schedule Trigger** — every 15 minutes.

**2. Set** `campaign_ids` = `[1298, 1313, 1315, 1145]`
Those four and only those four. 1008 and 1009 are the old campaigns the "Amy"
replier still answers; touching them creates two repliers on one thread.

**3. Split Out** on `campaign_ids` → one item per campaign.

**4. HTTP Request — fetch replies** (credential `Bison Consulti WS`)
```
GET https://send.leadgenjay.com/api/campaigns/{{ $json.campaign_ids }}/replies
    ?status=interested&per_page=15&page={{ $pageCount + 1 }}
```
Turn on **Pagination** → "Response Contains Next URL" is not available here, so use
*Pagination Mode: Update a Parameter in Each Request*, complete when
`{{ $response.body.meta.current_page >= $response.body.meta.last_page }}`.

**5. Split Out** on `data` → one item per reply.

**6. Filter** — drop the autoresponders:
```
{{ $json.automated_reply !== true }}
```

**7. Postgres / Data Table — dedupe**
Look up `reply_id` in `seen`. **If found, stop this item.** If not, insert it and
continue. Insert *before* the rest of the branch, not after, so a crash mid-run
can't double-prepare.

**8. HTTP Request — thread state**
```
GET https://send.leadgenjay.com/api/replies/{{ $json.id }}/conversation-thread
```

**9. IF — already answered**
```
{{ $json.data.newer_messages.filter(m => m.type === 'Outgoing Email').length > 0 }}
```
**True** → write to `queue` with `outcome = hold`, `note = "already answered by the
live replier on <date>"`, `status = held`. Stop.

This is the guard that actually matters. Someone else on the workspace answers
these threads within minutes. Everything downstream assumes this node ran.

**10. HTTP Request — the lead**
```
GET https://send.leadgenjay.com/api/leads/{{ $json.lead.id }}
```

**11. Code node — resolve, clean, classify**

```javascript
// Paste consulti-niche-filter-map.json into a Set node upstream, or read it
// from the list server at GET /api/niche-map.
const map = $('Niche Map').first().json;
const lead = $json.data;
const reply = $('Split Out Replies').item.json;

// --- the lead's own words, without the quoted thread underneath
function cleanReply(body) {
  const out = [];
  for (const line of (body || '').split('\n')) {
    const t = line.trim();
    if (t.startsWith('>')) break;
    if (/^(on |from:|-----original)/i.test(t) && /wrote:/i.test(t)) break;
    out.push(line);
  }
  return out.join('\n').trim().slice(0, 1500);
}

// --- niche comes off the lead's custom variables, in this order
const cv = {};
for (const c of lead.custom_variables || []) cv[c.name] = (c.value || '').trim();
let niche = null, source = null;
for (const k of ['signal_topic', 'niche', 'industry', 'client_niche']) {
  if (cv[k]) { niche = cv[k]; source = k; break; }
}

const text = cleanReply(reply.text_body);

// --- what the lead actually asked for overrides the campaign variable.
// Jeremy asked for "enterprise, above $500k in monthly revenue" and the
// variable queued him a list capped at 500 employees. Read the reply.
const MISMATCH = /much larger|larger list|bigger list|more than \d|only need|instead of|rather than|list of \d{3,}|\d{3,}\s*(of those|contacts|leads)|\$\s?[\d.,]+\s?[kmb]\b|\$[\d.,]{3,}|\b\d[\d.,]*\s?(k|m|mm|million|billion)\b|\benterprise\b|\bmid-?market\b|upwards of|at least \$?[\d,]|\b(annual|monthly) revenue\b|\bper (year|month)\b/i;
const QUESTION = /\?/;

let outcome, note = '', listFile = null, rows = 0;

if (MISMATCH.test(text)) {
  outcome = 'hold';
  note = 'lead named a size or revenue band the shelf list does not match; read the reply';
} else if (!niche) {
  outcome = 'ask';
  note = 'no niche variable on this lead';
} else {
  const k = niche.toLowerCase().trim();
  if (map.industry[k]) {
    listFile = k.replace(/[^a-z0-9]/g, '-').replace(/^-+|-+$/g, '') + '.csv';
    const shelf = $('List Manifest').first().json.lists[listFile];
    if (!shelf)            { outcome = 'build'; note = `no list at lists/${listFile}`; }
    else if (shelf.rows < 150) { outcome = 'hold'; rows = shelf.rows;
                                 note = `list has only ${shelf.rows} rows, floor is 150`; }
    else                   { outcome = 'ready'; rows = shelf.rows; }
  } else if (map.geo[k])    { outcome = 'build';
                              note = 'geo niche, needs their city/state and a per-lead pull'; }
  else if (map.intent[k])   { outcome = 'ask';
                              note = 'niche is a buying signal, not an industry'; }
  else                      { outcome = 'ask'; note = `unmapped niche "${niche}"`; }
}

return [{ json: {
  reply_id: reply.id, campaign_id: reply.campaign_id, lead_id: lead.id,
  email: lead.email, first_name: lead.first_name || 'there',
  company: lead.company, niche, niche_source: source,
  reply_text: text, outcome, note, list_file: listFile, rows,
}}];
```

**12. Switch** on `outcome` → four outputs: `ready`, `ask`, `hold`, `build`.

### ready branch

**13. HTTP Request — mint the link** (credential `List Server`)
```
POST https://files.nextwave.io/api/mint
{ "reply_id": "{{ $json.reply_id }}", "list": "{{ $json.list_file }}",
  "email": "{{ $json.email }}", "rows": {{ $json.rows }} }
```
→ returns `{"url": "https://files.nextwave.io/d/<token>"}`

**14. Code — render the body.** Column names get translated to human words, because
"linkedin_url" in a sentence reads like a database dump:

```javascript
const pretty = { first_name:'name', title:'title', company:'company',
                 linkedin_url:'LinkedIn', website:'website', phone:'phone',
                 city:'city', email:'a verified email' };
const cols = $('List Manifest').first().json
  .lists[$json.list_file].columns.map(h => pretty[h]).filter(Boolean);
const columns = cols.slice(0, -1).join(', ') + ' and ' + cols.at(-1);

const body = `Hi ${$json.first_name},

Here it is. ${$json.rows} verified contacts at ${$json.niche}, with ${columns} for each one:
${$('Mint').first().json.url}

It's yours to use however you like, for your own outreach or a client's. No strings.

I've also put a month of Consulti on us, so you can pull a list like this yourself whenever a client launch comes up:
{{GIFT_CODE}}

Anything you'd want cut differently, just say so and I'll redo it.`;

return [{ json: { ...$json, body, link: $('Mint').first().json.url } }];
```

Copy rules, all three learned the hard way: never the word **free** (use "on us"),
never an **em dash**, and never a row count the list doesn't actually have. We
shipped "78 contacts" on a 60-row file once.

`{{GIFT_CODE}}` stays a placeholder here on purpose. Gift links are single
redemption. Baking a code into a draft burns one per *draft* instead of one per
*send*, and the second lead to click a reused link gets a dead page. WF-2 claims a
code at send time.

**15. Postgres — insert into `queue`** with `status = 'pending'`.

### ask branch
Same as 14–15 but the body is the clarifying question, no link, no row count:

```
Hi {first_name},

Happy to pull it.

What kind of businesses do you want them to be? Give me the industry, and a city or
state if that matters, and I'll put the list together and send it over.

Either way, here's a month of Consulti on us so you can pull lists yourself in the
meantime:
{{GIFT_CODE}}
```

### hold branch
Insert into `queue` with `status = 'held'` and the note. No body rendered. These
need you to write them by hand.

### build branch
Insert into `queue` with `status = 'held'`, and insert the niche into a
`build_queue` table that WF-3 reads. The lead waits for the list, which is correct:
better a day's wait than a thin list.

**16. Slack / email notify** — only if `ready + ask > 0`. Link straight to the desk.
Don't notify on zero; a bot that pings you every 15 minutes to say nothing happened
is a bot you'll mute.

---

## WF-2 — Approve & Send (webhook)

This is the only workflow with a POST to Bison in it. Treat it accordingly.

**1. Webhook** — `POST /webhook/give-first-approve`, response mode "Last Node".

**2. IF — shared secret.** Compare a header against a credential. Anything else
→ respond 401 and stop. This URL can send email on your behalf.

**3. IF — killswitch.** Read a `settings` row `sending_enabled`. False → respond
`{"refused":"killswitch"}`. Your equivalent of `scripts/sender.off`, and the thing
you'll want at 2am when something looks wrong.

**4. Postgres — load the queue row** for `reply_id`.
Refuse unless `status = 'pending'`. This alone blocks double-clicks on Approve.

**5. Postgres — check `sent_log`.** Row exists → respond
`{"refused":"already sent once; one send per reply id, ever"}`. Belt and braces
with step 4, and this one is keyed in the database.

**6. Postgres — daily cap.** `SELECT count(*) FROM sent_log WHERE sent_at::date = current_date`.
Over 40 → refuse. A runaway loop that sends 300 emails from your own domains is an
unrecoverable event; a cap makes it a 40-email event.

**7. HTTP Request — re-check the thread.** Same call as WF-1 step 8. Minutes or
hours have passed since preparation and the live replier may have answered in
between. Any `Outgoing Email` in `newer_messages` → refuse, set `status = 'held'`.

**Do not skip this because WF-1 already checked.** WF-1 checked at preparation
time. This checks at send time. They are different moments and the second one is
the one that counts.

**8. HTTP Request — the reply record**
```
GET https://send.leadgenjay.com/api/replies/{{ $json.reply_id }}
```

**9. Code — resolve the sending mailbox**
```javascript
let senderId = $json.sender_email_id;          // often null
if (!senderId) {
  const inbox = ($json.primary_to_email_address || '').toLowerCase();
  senderId = $('Mailboxes').first().json[inbox];   // from the mailboxes table
}
if (!senderId) throw new Error(
  `the mailbox this lead replied to (${$json.primary_to_email_address}) is not a ` +
  `live sender in this workspace, so the thread cannot be answered from it`);
return [{ json: { ...$json, sender_email_id: senderId } }];
```
Terry Murphy is the reason this throws instead of guessing. He replied to a mailbox
that no longer exists in the workspace; there is no way to answer him in-thread and
the honest outcome is a refusal, not a send from a different address.

**10. Code — claim a gift code.** `UPDATE gift_codes SET claimed_by = $reply_id
WHERE claimed_by IS NULL LIMIT 1 RETURNING code`, then substitute it into the body.
No code available → refuse. Then assert the rendered body no longer contains
`{{GIFT_CODE}}`; if it does, refuse. A prospect receiving a literal `{{GIFT_CODE}}`
is worse than a prospect receiving nothing.

**11. HTTP Request — send** (credential `Bison Consulti WS`)
```
POST https://send.leadgenjay.com/api/replies/{{ $json.reply_id }}/reply
Body Content Type: Form-Data (multipart)
  message                      = {{ $json.body }}
  sender_email_id              = {{ $json.sender_email_id }}
  to_emails[0][email_address]  = {{ $json.email }}
```

**Settings on this node: Retry On Fail = OFF. Always Output Data = OFF.**
A retry re-mails the prospect. n8n defaults are fine for idempotent APIs and this
one is not.

The list travels as a **link in the body**, not an attachment. An attachment means
n8n holds a 43KB binary through the whole chain and re-sends it on every retry; the
link is revocable, it tells you whether they actually downloaded it, and it keeps
3,944 people's verified emails off any forwardable public URL.

**12. Postgres — write `sent_log`**, set `queue.status = 'sent'`.
Immediately, same branch, no delay. If this write fails you want to know while the
run is still open.

**13. Respond** `{"sent": true, "new_reply_id": ...}`.

**14. Error Trigger workflow** → set `status = 'error'`, store the response body,
notify you. An error after step 11 means the email may have gone out, so the row
reads `error` and you check the thread by hand rather than letting anything retry.

---

## WF-3 — Shelf top-up (nightly, 3am)

**1. Schedule Trigger** — daily.

**2. HTTP — refresh the mailbox map** (pagination on `page`):
```
GET https://send.leadgenjay.com/api/sender-emails?page={{ $pageCount + 1 }}
```
Upsert `email → id` into `mailboxes`. 292 live mailboxes last count. WF-2 step 9
depends on this being current.

**3. Postgres** — read `build_queue` plus every manifest list under 300 rows.

**4. Switch** on the niche's `endpoint` from the filter map:

### B2B route — `POST https://www.consulti.ai/api/v1/leads/search`
```json
{ "countries": ["United States"], "emailStatus": "good",
  "industries": ["..."], "empMin": 10, "empMax": 500,
  "page": 1, "size": 100 }
```
Paginate while `has_more`. Map each lead: `first_name`, `last_name`,
`job_title`→title, `company_name`→company, `linkedin_url`, `city`, `state`, `email`.
Drop rows with no email.

**Always send an employee cap.** Without `empMax` an agency owner gets the Fortune
500, which is not who they can sell to.

### Local route — `POST https://www.consulti.ai/api/v1/local-leads/search`
```json
{ "keywords": ["Car dealer"], "hasEmail": true,
  "states": ["TX"], "cities": ["Plano"], "page": 1, "size": 100 }
```
One request per keyword, each paginated to exhaustion, stopping only when the
**whole list** hits 300.

Do not divide 300 across the keywords. Widening cannabis from 2 keywords to 10 cut
the per-keyword budget from 150 to 30 and *shrank* the list from 144 rows to 102.

Drop rows with no `owner_name` — the copy promises a real name for every contact.
Dedupe on email and `google_place_id`.

**Local niches never come off the B2B industry filter.** Measured: the Automotive
industry filter returned 174/300 even auto-related, the rest tire makers and
General Motors.

**5. Code — drop chains.** Match company name and domain against a chain list. We
shipped a list containing Texas Roadhouse's founder, who died in 2021.

**6. Code — only write if the new pull is bigger.** `if (newRows.length <= currentRows) → skip`.
A top-up that returned 102 rows once overwrote a 144-row file and the original was
gitignored, so it was gone. Never overwrite a list with a shorter one.

**7. HTTP — upload to the list server**, which rewrites `list-manifest.json`.

**8. Notify** with what grew, what is still short, and what is still unbuildable.

Three things Consulti cannot filter on, no matter how the lead phrases it:
**revenue, religious or denominational affiliation, and intent signals.** When a
lead asks for one of those, the honest answer is the clarifying question, not a
list that quietly ignores half the brief. Carl's niche was unservable both ways:
2/90 on the local route, 6/500 on B2B. He got 78 merged rows and a reply that said
so.

---

## The guard table

Every one of these exists because something went wrong without it.

| Guard | Where | Refuses when |
|---|---|---|
| Allowlist | WF-1 #2 | campaign isn't one of the four |
| Autoresponder | WF-1 #6 | `automated_reply` is true |
| Seen-before | WF-1 #7 | reply already prepared |
| Thread answered (prepare) | WF-1 #9 | someone else replied |
| Row floor | WF-1 #11 | list has fewer than 150 rows |
| Size/revenue mismatch | WF-1 #11 | the reply names a band the list doesn't match |
| Shared secret | WF-2 #2 | header is wrong |
| Killswitch | WF-2 #3 | sending is switched off |
| Status | WF-2 #4 | row isn't `pending` |
| Send ledger | WF-2 #5 | reply id already in `sent_log` |
| Daily cap | WF-2 #6 | 40 already sent today |
| **Thread answered (send)** | WF-2 #7 | someone replied since preparation |
| Mailbox resolution | WF-2 #9 | the receiving mailbox isn't a live sender |
| Gift placeholder | WF-2 #10 | body still contains `{{GIFT_CODE}}` |
| No retry | WF-2 #11 | — (prevents a duplicate send) |

---

## Test plan

Do these in order. Don't skip to 5.

1. **WF-1 against one campaign with the Switch outputs disconnected.** Confirm it
   finds replies, resolves niches, and classifies. Nothing writes.
2. **Reconnect the branches.** Run again. Read every row in `queue` and check the
   outcome against the lead's actual words.
3. **WF-2 with the Bison POST node disabled.** Approve one row. Watch all nine
   guards run. Confirm it reaches the send node and stops.
4. **Point WF-2 at your own address.** Hand-insert a `queue` row whose email is
   yours, approve it, read what arrives. Check the link downloads, the row count
   in the copy matches the CSV, the gift code is a real URL, and there's no em dash.
5. **Approve one real lead.** One. Read the thread in Bison afterwards.
6. **Then let the schedule run.**

At step 5 you'll want to re-read `consulti-give-first-reply-agent.md` first — it has
the 28 real questions leads have asked and the three verbatim replies that worked.

## What stays manual

- The **Approve** click. By design.
- The **8 held leads**: Jesse wants a bigger list, Jeremy wants enterprise above
  $500k monthly revenue, Terry's mailbox is gone. No classifier handles these.
- **Turning off the old replier** on 1298/1313/1315/1145. Until that happens, WF-2
  step 7 is the only thing standing between a lead and two different replies from
  your company. It will hold leads rather than double-reply, which means a quiet
  trickle of `held` rows is the symptom of the old agent still being on.
