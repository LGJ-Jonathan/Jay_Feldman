# Consulti — Instagram Database Campaigns (copy)
**Rebuilt 2026-08-19.** Two audiences, two offers, three emails each, two A/B openers on E1.
Waits 3 / 4 days. Plain text, no open tracking, threaded follow-ups.
**Spam score: Great (0 hits).**

## Personalization rule for this build

**Every variable either ships with the Consulti list or is one Claygent homepage visit.**
No counts, no claims we cannot stand behind per lead. Verified fill rates against the
actual 9,465 and 4,197 records already pulled.

### Audience 1 — DTC brands

| Variable | Source | Fill | Fallback (REQUIRED) |
|---|---|---|---|
| `{FIRST_NAME}` | ships with list | 100% | — |
| `{COMPANY}` | ships with list | 100% | — |
| `{THEIR_STACK}` | list field `technologies` | 100% | `Shopify` |
| `{CREATOR_TYPE}` | static map from `industry` (below) | 100% | `Instagram creators` |
| `{THEIR_PRODUCT}` | **optional** Claygent, one homepage visit | — | *omit the clause entirely* |

`technologies` averages 8.2 entries per lead. **Pick in this order: Attentive → Klaviyo →
Shopify.** Attentive appears on 894 records and is the sharpest signal; Klaviyo covers 9,062;
Shopify 8,224 is the floor. Never print the raw array.

### `{CREATOR_TYPE}` map — from the `industry` field

| industry | CREATOR_TYPE |
|---|---|
| Apparel & Fashion | `fashion creators` |
| Cosmetics | `beauty creators` |
| Health, Wellness & Fitness | `fitness and wellness creators` |
| Sporting Goods | `fitness creators` |
| Food & Beverages | `food creators` |
| Luxury Goods & Jewelry | `fashion and lifestyle creators` |
| Retail / Consumer Goods | *(too vague — use Claygent or fall back to* `Instagram creators`*)* |

**Normalize case first.** The API returns both `apparel & fashion` and `Apparel & Fashion`
in the same result set. Lowercase-and-trim before mapping or roughly a third of the list
misses. Retail + Consumer Goods is ~2,300 of 9,465, so budget for the fallback on ~24%.

### Audience 2 — influencer practitioners

| Variable | Source | Fill | Fallback |
|---|---|---|---|
| `{FIRST_NAME}` / `{COMPANY}` | ships with list | 100% | — |
| `{THEIR_TITLE}` | list field `job_title` | 100% | `handle creator partnerships` |
| `{BIO_PHRASE}` | static map from `industry`, e.g. `ugc creator` | 100% | `ugc creator` |

`job_title` is the strongest variable here and it is free — the list was *selected* by title,
so "saw you handle influencer marketing" is accurate by construction, never a guess.

---

# AUDIENCE 1 — DTC brands · offer = sample list

## E1 variant A — the stack observation

**Subject:** `creator emails for {COMPANY}`

```
{Hi|Hey} {FIRST_NAME},

Saw {COMPANY} runs {THEIR_STACK}.

I can send you 100 {CREATOR_TYPE}, 10k to 500k followers, with their emails
attached. Not DM handles, real inboxes.

{Want them?|Want the list?}

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

## E1 variant B — the question open

**Subject:** `how {COMPANY} finds creators`

```
{Hi|Hey} {FIRST_NAME},

How does {COMPANY} find {CREATOR_TYPE} these days?

Asking because I can send you 100 of them with real emails attached instead of
DM handles. On us.

{Want them?|Worth a look?}

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

## E2 — thread reply, wait 3 days

**Subject:** `Re: creator emails for {COMPANY}`

```
{Hi|Hey} {FIRST_NAME},

The emails are verified, so the list is ready to send the day you have it.

{Want me to pull it?|Should I send it over?}

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

## E3 — new thread, wait 4 days · fallback = gifted month

**Subject:** `last one on the creator list`

```
{Hi|Hey} {FIRST_NAME},

Last one from me.

{Two options.|Either way works.} I send you the 100, or I gift you a month and
you pull whatever you want yourself. Nothing owed, not a rev share.

Reply with the word list and I will sort it.

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

---

# AUDIENCE 2 — influencer practitioners · offer = gifted month

## E1 variant A — the capability gap

**Subject:** `sourcing creators at {COMPANY}`

```
{Hi|Hey} {FIRST_NAME},

Saw you are the {THEIR_TITLE} at {COMPANY}, so this is your lane.

Can your current tool search what creators wrote in their bios? Most just filter
by the category tag Instagram assigned them.

Ours searches the bio text. I can gift you a month to try it.

{Want it?|Interested?}

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

## E1 variant B — the tool-agnostic open

**Subject:** `what {COMPANY} uses for creator search`

```
{Hi|Hey} {FIRST_NAME},

Every creator tool filters by category tag. None of them search the actual bio
text, which is where the intent sits.

Ours does, and every profile has a verified email on it.

I can gift you a month. {Interested?|Want it?}

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

## E2 — thread reply, wait 3 days · de-escalate to a file

**Subject:** `Re: sourcing creators at {COMPANY}`

```
{Hi|Hey} {FIRST_NAME},

{Simpler option.|Easier version.} Skip the login. Send me one phrase your ideal
creator would have in their bio and I will run it and send the file over.

One reply and it is done.

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

## E3 — new thread, wait 4 days

**Subject:** `closing the loop`

```
{Hi|Hey} {FIRST_NAME},

Last one from me.

The month is still yours if you want it, or send me a bio phrase and I will just
run it myself. Nothing owed either way.

{Which one?|Either work?}

{Best|Cheers},
{SENDER_EMAIL_SIGNATURE}
```

---

## Rules held in this copy

- **No unverifiable numbers.** No database size, no per-lead creator count, no "500M+"
  (the site says 10M+). The only figures are the follower band, which is a filter we set.
- **No "free" and no "no cost."** Both are spam-flagged. "On us", "nothing owed",
  "I can gift you a month".
- **"Nothing owed, not a rev share"** in A1/E3. Nova Hiring read C1's "on me" as
  performance-based; this closes that door.
- **No geo claim.** The country filter is broken, so nothing implies US-only creators.
- **No em dashes.** Plain, casual.
- **Every variable has a fallback**, so a thin record cannot render a broken sentence.

## Before launch

1. Normalize `industry` case before applying the CREATOR_TYPE map.
2. Render 20 sample emails per variant and read them cold. C1's Ovalis bug was only
   visible in render, never in the template.
3. Cap contacts per company domain.
4. Fulfilment must accept a narrowing request. C1's interested leads asked for filters
   before delivery, and the same will happen here.
