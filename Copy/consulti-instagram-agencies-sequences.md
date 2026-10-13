# Consulti Creator + Instagram DB: Agency Sequences

**Pitching:** the Consulti creator database (podcasts 131,690 + YouTube 50,485 = 182,175, email on 100%, measured 2026-08-19) plus the Instagram database (bio keyword search, follower range, engagement sort, verified email on the contactable slice).
**Platform:** Email Bison. Plain text, open tracking off, 2 variants on every step.
**Cadence:** E1 → E2 (same thread, +3 days) → E3 (new thread, +4 days).
**Every email:** Mailmeteor Great (0), no dashes, `{FIRST_NAME}` is the only merge field.

| Segment | Audience | Size | Status |
|---|---|---|---|
| A | Clipping, video editing, YouTube and podcast services | ~3.5k | Written 2026-09-16, de-tokenized 2026-10-05 |
| B | Talent management and influencer agencies | ~3.5k | To write |
| C | Personal branding and social media management | ~8k | To write |

---

# Segment A: clipping, video editing, YouTube and podcast services

## No enrichment needed (updated 2026-10-05)
`{CREATOR_TYPE}` and `{NICHE_COUNT}` were removed from every email: the Clutch scrape could not fill them reliably, and a blank token renders a broken sentence. The two-tier split is gone with them, because there is nothing left to tier on.

**The only tokens in this campaign:**

| Token | Source |
|---|---|
| `{FIRST_NAME}` | Ships with the list, built into Bison |
| `{SENDER_EMAIL_SIGNATURE}` | Set per mailbox in Bison |

Every lead can receive every variant, so Bison's random variant assignment is safe.

### E1 A/B test: 3 pain points (launch these)
Same opener, same give (50 verified, on us), same CTA. **Only the pain changes**, so the test reads cleanly.

| Variant | Pain | Hypothesis |
|---|---|---|
| 1 | Access: a six-figure database with contact info that goes directly to the creator, plus Sagrada P.S. | Direct access plus proof |
| 2 | Can't pay: small creators reply but can't afford editing | Wasted pitching; speaks to revenue |
| 3 | Churn: retainer pauses when a creator stops posting | Pipeline fear; strongest for retainer-based shops |

**How to read it:** score genuine positives per 1,000 contacted, not reply rate. At ~1,150 contacts per arm, only a large gap will show, so treat the result as directional. Follow-ups use new angles (platform pick, bio search, gifted month, marketplace pain), so none repeat an E1 pain.

#### Variant 1: access
```
Subject: {creators to pitch|i have a list for you|influencers}

{Hi|Hey|Hello} {FIRST_NAME}, saw the sick {reels|shorts|YouTube videos} you edit.

We bought out a six-figure database of Instagram creators, YouTubers and podcasters, with proprietary contact info that goes directly to the creator.

I can pull you 50 in whatever niche you like editing for, each with a verified email. On us.

{Want them?|Want the list?|Should I pull them?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}

P.S. Sagrada AI booked 13 meetings in 1 week with this data.
```

#### Variant 2: can't pay
```
Subject: creators who can pay

{Hi|Hey|Hello} {FIRST_NAME}, saw the {reels|shorts|YouTube videos} you edit for creators.

{Curious|Wondering} how many of the creators who answer your pitches can actually afford editing?

I can pull you 50 with an established audience, filtered by followers, each with a verified email. On us.

{Want them?|Want the list?|Should I pull them?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

#### Variant 3: churn
```
Subject: when a creator stops posting

{Hi|Hey|Hello} {FIRST_NAME}, saw the {reels|shorts|YouTube videos} you edit for creators.

{Curious|Wondering} what happens to the retainer when one of your creators stops posting for a month?

The work usually pauses with them, so the next client has to be lined up before that happens.

I can pull you 50 creators to keep in your pipeline, each with a verified email. On us.

{Want them?|Want the list?|Should I pull them?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### E2 variant A: pick a platform (same thread, +3 days)
```
{Hi|Hey} {FIRST_NAME},

{Still happy to pull those 50.|Happy to pull those 50 whenever.} Want Instagram creators, YouTubers or podcasters?

Tell me which and I will send the list over.

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### E2 variant B: bio search (same thread, +3 days)
```
{Hi|Hey} {FIRST_NAME},

One thing I left out. You can search Instagram by what creators write in their bio.

{Want me to run it?|Should I run that search?|Want me to pull it?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### E3 variant A: gifted month (new thread, +4 days)
```
Subject: your own creator search

{Hi|Hey|Hello} {FIRST_NAME},

Last idea from me. Instead of a single list, I can gift you a month of pro and you run the search yourself.

Instagram creators, YouTubers and podcasters in one place, with an email on each one. Nothing owed after.

{Want it?|Interested?|Should I set it up?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### E3 variant B: skip the marketplace (new thread, +4 days)
```
Subject: skip the marketplace

{Hi|Hey|Hello} {FIRST_NAME},

Last note from me. Bidding on Upwork against cheaper editors is a race to the bottom, and going straight to the creator's inbox skips it.

If that ever sounds useful, reply with a niche and I will send you 50 creators from it.

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

---

## Spare openers (not in the launch test)
Keep these for round two, or swap one in if a launch variant dies.

### Spare 1: finding the next client
```
Subject: creators to pitch

{Hi|Hey|Hello} {FIRST_NAME}, saw the {reels|shorts|YouTube videos} you edit for creators.

{Curious|Wondering} how you're finding the next few to pitch, since that part can take a lot of time?

Their emails are hard to track down, and DMs {usually go unanswered|mostly go unanswered|tend to go unanswered}.

I can pull you 50 creators, each with a verified email. On us.

{Want them?|Want the list?|Should I pull them?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### Spare 2: Sagrada proof
Confirm before launch: the 13 meetings came from a Consulti-pulled list, and Phoebe is OK with Sagrada being named.
```
Subject: 13 meetings with creators

{Hi|Hey|Hello} {FIRST_NAME}, saw the {reels|shorts|YouTube videos} you edit for creators.

Sagrada AI pitches the same kind of people you do: creators and experts sitting on long videos that nobody turns into clips.

They booked 13 meetings in under 2 weeks {emailing|reaching out to} a list pulled from our platform.

I can pull you 50 the same way, each with a verified email. On us.

{Want them?|Want the list?|Should I pull them?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### Spare 3: how they find clients
```
Subject: creators to pitch

{Hi|Hey|Hello} {FIRST_NAME}, how are you finding creators to pitch your editing to these days?

DMs to creators {tend to sit|usually sit|mostly sit} in message requests for weeks.

We have 180k+ podcasters and YouTubers with an email on every one, plus Instagram creators you can search by what they wrote in their bio. I can pull you 50 who fit your editing, on us.

{Want them?|Want the list?|Should I pull them?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### Spare 4: the give up front
```
Subject: creators to clip

{Hi|Hey|Hello} {FIRST_NAME},

Podcasters and YouTubers are already making long videos. {Plenty of them|A lot of them|Many of them} have nobody cutting those into clips for Instagram.

I can pull you 50 of them with a verified email on each, from podcasts, YouTube or Instagram. On us.

{Want the list?|Should I send them over?|Want them?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### Spare follow-up: pick a niche and platform (E2)
```
{Hi|Hey} {FIRST_NAME},

{Still happy to pull those 50 creators.|Happy to pull those 50 creators whenever.} Tell me the niche you like editing for, and whether you want podcasters, YouTubers or Instagram creators.

{Which should I pull?|What should the list be?|Which niche should it be?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### Spare follow-up: audience size (E2)
```
{Hi|Hey} {FIRST_NAME},

One detail I left out. You can filter by audience size, so every creator on the list is big enough to hire an editor.

{Want me to pull it?|Should I send it over?|Want the 50?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### Spare breakup: reply with a niche (E3)
```
Subject: clips for creators

{Hi|Hey|Hello} {FIRST_NAME},

Last note from me. If finding creators to pitch ever becomes the bottleneck, reply with a niche and I will send you 50 podcasters or YouTubers from it.

{If not, no worries.|If the timing is wrong, no worries.|No pressure either way.}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

## Before launch (Segment A)
- [ ] **"180k+ podcasters and YouTubers"** rests on the 2026-08-19 count (182,175). Re-check the live count before launch, and never use the "847k" figure.
- [ ] **"Bought out a six-figure database":** confirm with Jay that this is accurate and sayable.
- [ ] **Sagrada P.S. in variant 1:** confirm the 13 meetings came from a Consulti-pulled list and that Phoebe is OK with Sagrada being named. If not, cut the P.S. and run variant 1 without it.
- [ ] **Variant 2 "filtered by followers"** is confirmed on Instagram only. Spare 2's "filter by audience size" needs the same check on the creator endpoint; if there is no subscriber/listener filter, change it to "follower range on Instagram".
- [ ] **Fulfillment:** a yes gets 50 podcasters/YouTubers from `/creator-leads/search` (always has email). A platform or niche reply gets that search. Instagram asks use `/instagram/search` with `bioKeywords` + `emailStatus: good`.
- [ ] **`/creator-leads/search` silently ignores unknown fields** and bills for unfiltered rows. Smoke-test every filter at small size first.
- [ ] **No geo claims.** The Instagram country filter is broken.
- [ ] **No dedupe on Instagram or creator endpoints.** Track which creators went to which agency.
- [ ] **Sender identity:** the signature name must match the From name.
