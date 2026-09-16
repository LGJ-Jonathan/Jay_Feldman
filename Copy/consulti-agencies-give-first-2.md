# Consulti Agencies - Give-First 2

**Built from:** campaign 1145 `Consulti Agencies - Give-First (8/22) Shara - optimizations`. The winning opener (step 7164) got 8 of the 14 real positive replies.
**Audience:** small marketing and ad agency owners
**Date:** 2026-09-16

## Before launch
- [ ] Run Clay enrichment for `{CLIENT_NICHE}` (see Enrichment fields below) and `{SERVICE}` (main service, lowercase, e.g. "SEO", "paid ads", fallback `marketing`)
- [ ] Re-verify every 300-contact list before sending it
- [ ] Enrich `{COWORKER_NAME_2}` for Variant B (one other person at the same domain, first name only, not the lead). Route leads without one to Variant A
- [ ] Confirm the gifted month of Consulti is still available and have the gift link ready for Email 3 yeses
- [ ] Pre-build one verified 300-contact list per `{CLIENT_NICHE}` value before launch (after Clay, group leads by niche; also build a `small businesses` list for the fallback). Re-verify each list the week it goes out.
- [ ] Reply to a yes by sending the matching niche list right away, no qualifying question: "Here you go: [link to {CLIENT_NICHE} list]. 300 verified contacts, ready to load. Works for pitching new {CLIENT_NICHE} clients or for a client campaign in that space. Let me know how it lands."

---

## Email 1 (day 0)

### Variant A: original winner (campaign 1145, step 7164, body unchanged)
```
Subject: {{FIRST_NAME}, a list for one of your clients|{CLIENT_NICHE} list|list of {CLIENT_NICHE} for {COMPANY}}

{Hi|Hey} {FIRST_NAME}, noticed {COMPANY} runs outbound for clients. {My guess is sourcing the list is what slows a launch down.|My guess is the list is the part that slows a launch down.}

I can {put together|pull together} 500 verified prospects for one of them and send it over, on me.

{Want me to?|Want me to pull it?}

{SENDER_EMAIL_SIGNATURE}
```

### Variant B: right-person opener
Only send to leads where Clay found a coworker (one other person at the same company, first name only). Leads without one get Variant A.
```
Subject: {{FIRST_NAME}, a list for one of your clients|{CLIENT_NICHE} list|list of {CLIENT_NICHE} for {COMPANY}}

{Hey|Hi} {FIRST_NAME}, not sure if this one is for you or if I should {reach out to|ask} {COWORKER_NAME_2} instead.

I can pull 300 verified contacts at {CLIENT_NICHE} for {COMPANY}, on us. {Enough to land your next client or fill a client campaign, without the hours of sourcing.|Use them to land your next client or for a client campaign, and skip the hours of sourcing.}

{Should I send them over?|Interested?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

---

## Email 2 (3 days later, same thread)

### Variant A: what's in the list
```
{Hi|Hey} {FIRST_NAME},

{In case it's useful|Quick follow up}, here's what's in the {CLIENT_NICHE} list: name, title, company, LinkedIn, city and a verified email for each contact.

{No pressure at all, the list is yours if you'd like it.|No pressure, happy to send the list over if it would help.}

{Would you like it?|Would that be helpful?}

{Best|Cheers|Talk soon},
{SENDER_EMAIL_SIGNATURE}
```

### Variant B: what's in the list + minutes vs hours
```
{Hi|Hey} {FIRST_NAME},

{In case it's useful|Quick follow up}, here's what's in the {CLIENT_NICHE} list: name, title, company, LinkedIn, city and a verified email for each contact. {A list like this takes minutes to pull in Consulti, not hours of sourcing from different tools.|In Consulti it takes minutes to pull, instead of hours of piecing it together from different sources.}

{No pressure at all, the list is yours if you'd like it.|No pressure, happy to send the list over if it would help.}

{Would you like it?|Would that be helpful?}

{Best|Cheers|Talk soon},
{SENDER_EMAIL_SIGNATURE}
```

## Email 3 (5 days later, same thread)

Value: a gifted month so they can pull their own lists whenever it suits them. Per client rules: "gift you a month", never "free".

### Variant A
```
{Hi|Hey} {FIRST_NAME},

Last note from me. The {CLIENT_NICHE} list is still yours. Or if you'd rather pull your own, I can gift you a month of Consulti {so you can pull a list whenever a client launch comes up.|so the next client list is a few clicks, not a few hours.}

{Want the list, the month, or should I leave it here?|List, month, or leave it here?}

{Best|Cheers|Talk soon},
{SENDER_EMAIL_SIGNATURE}
```

### Variant B
```
{Hi|Hey} {FIRST_NAME},

Last note from me. The {CLIENT_NICHE} list is still yours, or local owners with direct emails by city if that's more useful. If you'd rather pull your own, I can gift you a month of Consulti {so you can pull a list whenever a client launch comes up.|so the next client list is a few clicks, not a few hours.}

{Want the list, the month, or should I leave it here?|List, month, or leave it here?}

{Best|Cheers|Talk soon},
{SENDER_EMAIL_SIGNATURE}
```

---

## Parked Email 1 variants (not in this launch)

### Time pain
```
Subject: {{FIRST_NAME}, a list for one of your clients|{CLIENT_NICHE} list|list of {CLIENT_NICHE} for {COMPANY}}

{Hi|Hey|Hello} {FIRST_NAME}, saw {COMPANY} does {SERVICE} for {CLIENT_NICHE}.

{My guess is|Guessing|I'd bet} sourcing a clean list of {CLIENT_NICHE} eats a few hours every time.

I can pull you 300 verified contacts at {CLIENT_NICHE} from our platform, on us. {Use them to land your next client or for a client campaign.|Use them for your own outreach or a client's.|Yours to use however you like.}

{Want them?|Want me to pull them?|Interested?}

{Best|Cheers|Thanks},
{SENDER_EMAIL_SIGNATURE}
```

### Right-person opener, friendlier version
Same routing as Variant B (only leads with a coworker name).
```
Subject: {{FIRST_NAME}, a list for one of your clients|{CLIENT_NICHE} list|list of {CLIENT_NICHE} for {COMPANY}}

{Hey|Hi} {FIRST_NAME}, {not sure if this is more up your alley or {COWORKER_NAME_2}'s|wasn't sure if this is more for you or {COWORKER_NAME_2}}, so I figured I'd start with you.

I'd be happy to pull 300 verified contacts at {CLIENT_NICHE} for {COMPANY}, on us. {Could be handy for landing your next client or a client campaign, and saves you the hours of sourcing.|Might come in handy for your next client or a client campaign, minus the hours of sourcing.}

{Want me to send them your way, or would {COWORKER_NAME_2} be the better fit?|Should I send them to you, or is {COWORKER_NAME_2} the better person?}

{Thanks|Cheers|Best},
{SENDER_EMAIL_SIGNATURE}
```

---

## Lead lists (decided 2026-09-16)

Based on the 14 interested replies in campaign 1145. Two lists, built in **GetLeads** (free exact counts, keyword filters on LinkedIn About/headline, `exclude_domains`). Industry names below must be confirmed with `get_available_values` before counting.

### Overlap rules (apply in this order)
1. **Suppression first:** drop every email and every company domain in `Leads/consulti-suppression-emails.csv` / `Leads/consulti-suppression-domains.txt` (everyone already emailed from the Consulti workspace plus the July master list).
2. **List 2 wins ties:** anyone who matches the List 2 title/headline keywords goes to List 2 only. List 1 excludes those titles.
3. **One segment per company domain:** after both exports, dedupe by email, then by domain. A domain in List 2 is removed from List 1.
4. **Max 2 contacts per domain**, owners first.

### List 1: small full-service and digital agencies
- Industries: Advertising Services, Marketing Services
- Exclude industries: Public Relations and Communications Services, Business Consulting and Services, Printing Services, Staffing and Recruiting, Real Estate
- Headcount (hard cutoff): `employee_profiles_on_linkedin_min: 2`, `max: 25`
- Titles: Owner, Founder, Co-Founder, President, CEO, Principal, Managing Partner
- Exclude titles: fractional, consultant, advisor, coach, freelance, public relations, PR, billboard, print, in-house roles (Marketing Manager, Director of Marketing)
- Countries: United States
- `company_description` (optional narrowing): digital marketing, advertising agency, full-service, SEO, PPC, paid ads, web design, social media
- Email status: VALID

### List 2: fractional CMOs and small consultants
- Industries: Business Consulting and Services, Strategic Management Services, Marketing Services
- Headcount (hard cutoff): `employee_profiles_on_linkedin_min: 1`, `max: 10`
- `linkedin_headline` OR `job_titles` contains: fractional CMO, fractional marketing, marketing consultant, growth consultant, business growth consultant, go-to-market consultant, AI automation, marketing advisor
- Seniority: Owner / Founder / C-Team
- Exclude industries: Human Resources Services, IT Services and IT Consulting, Financial Services, Accounting
- Countries: United States
- Email status: VALID

### Enrichment fields
| Field | Rule |
|---|---|
| `CLIENT_NICHE` | Specific industry on the site, plural lowercase ("dental practices"). If only a city or region: "{City} businesses". Otherwise `small businesses`. |
| `NICHE_TYPE` | `industry`, `geo` or `generic` |
| `SERVICE` | Main service, lowercase. Full-service agencies get `marketing`. |
| `SEGMENT` | `agency` or `consultant` |
| `QUALIFIED` | `no` if the site is dead or parked, PR-only, in-house or software, or says closed/acquired |

### Fulfillment
Automation reads `CLIENT_NICHE` and `NICHE_TYPE` from a positive reply's lead, pulls 300 verified contacts from Consulti, and delivers the list (owner building this).
