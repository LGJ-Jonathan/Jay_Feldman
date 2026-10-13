# LGJ Primary Workspace — C1 & C2 Latest Campaigns Analysis
**Source:** LGJ primary Bison workspace (`send.leadgenjay.com`, key `487|…`)
**Campaigns:** C1 – IT Services & MSPs (id 1019) · C2 – Recruiting & Staffing (id 1020) — both created 2026-07-23
**Date analyzed:** 2026-08-19

> These are the 2 latest LGJ-own outbound campaigns, targeting the segments we identified as best-converting (IT/Software + Staffing). This is the "free list of your ideal clients" DFY funnel — value-first, no call.

---

## Performance

| Campaign | Sent | Replies | Interested | Interested rate | Leads loaded |
|----------|------|---------|-----------|-----------------|--------------|
| **C1 – IT Services & MSPs** (1019) | 830 | 20 | **12** | **1.44%** | 13,042 |
| **C2 – Recruiting & Staffing** (1020) | 3,007 | 51 | **7** | 0.23% | 7,509 |

C1 converts ~6× better per send. Both far exceed the ~0.4% interested benchmark from the Jan–Jul Instantly analysis (esp. C1).

---

## THE OFFER (both campaigns)

Value-first, zero-friction. Same winning structure as the top Consulti campaigns — lead with the give:

**Primary offer:** *"I can pull you a list of 500 [their target clients], verified and ready to email this month. On me. Want me to pull it?"*

**Alt variant offer:** *"I spent time on [COMPANY] and wrote you a short email campaign for [their offer]. OK if I send it over? Free."*

Sequence: 3 base steps + 5 A/B variant openers each. Waits 3/5/3 days. 3-email core with a hard "last one, reply and it's yours" close that also name-drops the 20k+ founder community.

---

## PERSONALIZATION — the key differentiator

| | C1 – IT/MSP | C2 – Staffing |
|---|---|---|
| Variables used | `{COMPANY}`, `{FIRST_NAME}`, **`{THEIR_AUDIENCE}`, `{THEIR_SERVICE}`, `{THEIR_OFFER}`** | `{COMPANY}`, `{FIRST_NAME}` only |
| Depth | Deep — AI-researched per company website | Light — generic "roles you fill" |
| Result | 1.44% interested | 0.23% interested |

**Sample C1 personalization values (AI-generated per lead):**
| Company | their_audience | their_service | their_offer |
|---|---|---|---|
| masterIT | municipal leaders | managed IT services | your proactive IT support |
| Wolfpack | cybersecurity professionals | cybersecurity consulting | your tailored training programs |
| Blue Sentry | CIOs | execution and governance | your defined outcomes |
| IronOrbit | IT directors | cloud-based IT services | your managed IT solutions |

**Takeaway:** the deep `{THEIR_AUDIENCE}` personalization is what makes C1 feel bespoke and drives the 6× lift. C2 is missing it.

---

## ⚠️ TWO COPY/LIST BUGS FOUND IN C1

1. **The list is mislabeled.** The `their_audience` values expose that "IT Services & MSPs" is actually full of **AI startups and mixed B2B services** — Nova Hiring (recruiters), Wildcard (ecommerce), HeyLina (relationship coaches), Valor AI (veterans), Sartori (fashion), Orbis (academic research). The personalization masks the messy list because each email still reads tailored.
2. **MSP-specific copy misfires on non-MSPs.** Lines like "signing new managed services clients" and the `{THEIR_OFFER}` insert break when the lead isn't an MSP. Ovalis Group replied: *"'that should pull in some salesforce consultants' ???? What do you mean?"* — a visibly broken template render.

---

## INTERESTED THREADS — what they said

### C1 – IT/MSP (12 interested)
| Company | Title | Reply gist |
|---|---|---|
| Altivum | — | **"Definitely interested in that list of 500 veterans. Go ahead and put it together."** (cleanest yes) |
| OptixLog | — | "Sure, send it over!" |
| Orbis Scientia | CEO/Founder | "Sure send the list. Let's see what it has." |
| Valor AI | — | **"If you could get me one paying customer I'll buy whatever you're selling."** |
| Evanthys | — | "Would you be able to take **ICP input to qualify the list** before sending? Coordinate with our CGO." |
| Nova Hiring | Founder/CEO | "What's the **payment/share model**?" (read it as rev-share) |
| Plobyte | — | "Email has rarely worked. Used Apollo + Clay, nothing turned out. You can send me [the list]." |
| Wildcard / PLX / HeyLina | CEOs | "How's it work?" / "Sure" / "Why not" |
| Sartori AI | — | Pass — founder-led outreach, not broad email |

### C2 – Staffing (7 interested — all genuine recruiting firms)
| Company | Title | Reply gist |
|---|---|---|
| Global Recruiters (Greenwood) | — | **"Yes, let's see what you have. If you help me you'll have a real success story for YouTube, as I'm nearly out of business."** 🔥 hottest lead |
| Global Recruiters (Denver) | — | **"Sure — P+C Insurance Product Managers"** (handed exact niche) |
| MorningStar Recruitment | — | "Can you pull by **revenue 20M–250M, 20–200 employees, manufacturing/fabrication/automation**?" (wants filters) |
| Benaiah Consulting | Managing Partner | "Sure, I'd love to see what you do." |
| Spherion | — | "Yes please tell me more." |
| CareerBridge IT | President/CEO (US Army ret.) | "Happy to learn more." |
| Talent Insight Search | Managing Director | "Not now, but will need to ramp up BD soon." (softer) |

**Pattern:** C2 recruiters are **highly qualified and self-identify their niche unprompted** — they hand you the exact ICP to fulfill against. Very easy yes + easy fulfillment.

---

## RECOMMENDATIONS

1. **Add deep personalization to C2.** It's running light (company + first name). Add `{THEIR_AUDIENCE}`-style vars ("companies hiring [the exact roles they place]") to push it toward C1's 1.4% rate.
2. **Clean or relabel C1's list.** Either filter to real MSPs, or make the copy audience-agnostic so "managed services clients" doesn't misfire.
3. **Fix the `{THEIR_OFFER}` template render** — it produced a broken sentence (Ovalis "????"). QA the variant that inserts it.
4. **Fulfillment must support ICP filters** — multiple interested leads asked to narrow by revenue/vertical/size before delivery. Build that into the list-pull step.
5. **Respond to hot threads fast** — several interested replies (esp. "nearly out of business") are time-sensitive and may be sitting unanswered. Prioritize the clean yeses (Altivum, both Global Recruiters, MorningStar, Benaiah, Orbis).
6. **Watch the rev-share read** — Nova asked "payment/share model?" The "on me / free" framing sometimes reads as performance-based; clarify it's a free sample of the platform data.

---

## One-line takeaway
**The winning machine = value-first "free list of 500 [their exact ideal clients]" + deep per-company personalization. C1 proves the personalization lift (6×); C2 proves the audience (staffing self-qualifies). Merge them: C1's personalization depth onto C2's cleaner staffing list.**
