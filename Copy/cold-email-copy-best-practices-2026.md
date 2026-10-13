# Cold Email Copy: Best Practices and Options (2026)

Compiled 2026-09-16 for the new Consulti campaign. Two inputs:

1. **Web research** on 2025–2026 practitioner data (Instantly, Smartlead, Saleshandy, Hunter, Belkins, Gong, Clay/Nowoslawski, Alex Berman, lemlist). Vendor numbers promote the vendor, so treat them as direction, not truth.
2. **Our own copywriting skills**: cold-email-copywriting (plus the open-rate playbook and copy-constraints), pc-formula (and its when-to-use data), cold-email-strategy, cold-email-ab-testing, cold-email-signals, clay-personalization, hormozi-tips, mailmeteor-spam-check, spintax-campaign-relaunch, brand-voice. These carry LGJ's measured data.

Where the web and our own data disagree, **our data wins**. It comes from our own infrastructure and our own ICP.

---

## 1. Where everything agrees

| Area | Rule | Evidence |
|---|---|---|
| Length | E1 **50–80 words**, hard cap 100 | Instantly top 10% under 80; Saleshandy 50–80; skill target 75 |
| Reading level | Grade 3–6. Short lines with white space, never a block of text | Lavender: grade 3–5 gets +36% replies; Jay flagged "blob" twice |
| Format | Plain text. No images, attachments, or HTML | Every source |
| Links | **Zero links in E1**, at most 1 in follow-ups | Skills + Mailshake/Unify 2026 |
| Tracking | Open and link tracking **OFF** | Hunter: 7.4% replies with tracking off vs 4.4% on |
| CTA | **One question, interest-based, answerable with "yes"** | Gong 304k emails; Saleshandy: soft CTAs get +78% positive; LGJ: a meeting ask in E1 **halves positives** (0.66 vs 1.42 per 1k) |
| Offer | **Give before you ask** (value-first, lead magnet, sample) | Consulti value-first beat ask-first **2.4x**; C1 give-first was the best angle in either workspace (1.45% interested); Hormozi |
| Pain | Specific, with a **number or a recency marker**. Never generic | Timeline hook 10.0% reply, numbers 8.6%, generic problem 4.4% (worst) |
| AI copy | AI finds the signal and writes at most one line. A human writes and edits the body | Hunter: AI emails bother 69% of decision makers; Berman: fully AI emails 0.3% vs 9.9% with one AI line |
| AI tells | **No em dashes, en dashes, or `--`**. No "I noticed / I came across / Hope this finds you well" | Skill lint hard-fails on dashes |
| Lists | Small, tight segments, **1 contact per company** | Hunter: lists of 21–50 get 6.2% vs 2.4% for 500+; 1 per company 5.1% vs 3.5% for 3+ |
| Titles | Owner / Founder / CEO. Directors and managers are off by default | Positive share: founders 50%, directors 27%, managers 24% |
| Company size | 1–10 employees first, then 11–50. 51–200 is hardest | Positive share: 1–10 = 57%, 51–200 = 28% |

---

## 2. Subject lines

**Do**
- **2–5 words**, lowercase or sentence case (casing barely matters, per Belkins).
- Sound like **a vendor, client, or friend**, not a salesperson: "Found a pixel issue", "Who set up your tracking?", "NAME, it's Austin".
- Tie the bait to what's actually in the email.
- A question or a personal reference both help (Belkins: 46% open).
- Follow-ups thread under the same subject. Bison adds `Re:` itself when `thread_reply:true`, so don't type it.

**Don't**
- **"quick question" / "quick q"**: banned. It scores 0.64 vs 1.36 positives per 1k in our data, Hunter's 2026 data shows 2.5% replies, and Bison activation blocks it.
- Research flex ("Curious about [Company]'s recent…").
- Urgency or hype words, ALL CAPS, jargon.
- Heavy spintax. Keep subjects to about 2 spin slots.

---

## 3. First line (it is also the preview text)

The prospect sees **only the subject and first line** before deciding to open, so the first line's job is to earn the open.

| Pattern | Example |
|---|---|
| Curiosity / confusion | "Did you ask for this LTL quote from FedEx?" |
| Show-me question | "Does this look like your latest shipping quote?" |
| Fix framing | "We fixed your LTL shipping quote." |
| Diagnostic claim | "I don't think your server-side tracking is set up correctly." |
| Warm / familiar (no-hook offers) | "Hope all's well, my friend." |
| Signal (signal campaigns only) | "Looks like you're [event]. Usually that means [insight]." |

- **Pain goes in sentence 2**, not the opener. Turn the pain into a hook, then explain it.
- **2026 wrinkle:** Gmail now shows Gemini AI summaries of threads. Once the email is opened, the value should be plain within the first 2 lines, because a summary strips curiosity tricks.

---

## 4. Body formulas: the options menu

Pick based on **what you actually have**, not on taste.

| Formula | Shape | Words | Needs | Ask size | Best for |
|---|---|---|---|---|---|
| **P.C.** | Pain → CTA | 35–60 | A hard per-prospect signal or a measured defect | Interest only ("Want more info?") | High volume, low-ticket, strong signal |
| **P.E.C.** | Pain/fear → named case study → CTA | 80–120 | A named, comparable client result | Permission ("Mind if I send times?") | Considered buys, skeptical or enterprise buyers |
| **P.P.C.** | Pain → **a real tip they can use today** → CTA | 70–95 | A genuinely useful give plus N more ideas ready | Direct in theory, **soft in practice** (see conflicts) | **LGJ default**: expertise-led and data offers; agencies |
| **Value Gift / Reverse Lead Magnet** | Hook → "I built/pulled X for you" → "want it?" | 50–80 | A deliverable you can actually produce (sample list, audit) | Yes to receive | **Data/list products (Consulti)** |
| **Proof Machine** | Hook → best result → CTA | 60–90 | Real numbers | Interest | Skeptical prospects |
| **Pain Dagger** | Surgical pain question → fix → CTA | 50–80 | A precise, non-generic pain question | Interest | Actively struggling prospects |
| **No-hook personality** | Warm opener → honest "we haven't met" → tiny ask → PS de-risk | 40–70 | Nothing: no proof, no magnet | "Mind if I send my cell?" | Commodity services with no differentiator |
| **AI specificity line** | Static copy + "I think we can help you {{specificity_line}}" | +1 line | Company description + a locked client offer block | Any | Making a generic offer feel custom without faking research |
| **Nowoslawski 5-part** (web) | Context → problem/solution → cost of inaction → proof → light CTA | ~100 | Signal + proof | Light | Signal campaigns |
| **Josh Braun 4T** (web) | Trigger → neutral question → third-party proof → ask | ~80 | Trigger + proof | Soft | Same as above |

**Useful extras from the skills**
- **Give the fix, not a description of your process.** Good: "Can I send you the list?" Bad: "Mind if I send a rundown of how we work?"
- **PS de-risk:** "PS: if you already have someone you trust, no worries."
- **Hormozi value equation:** raise the dream outcome and the likelihood it works; lower the time delay and the effort. No fabricated proof; use `[placeholder]` instead.
- **Rough "you" to "I" ratio of 2:1** (Berman).

---

## 5. Sequence structure

| Step | Day | Thread | Job | CTA |
|---|---|---|---|---|
| E1 | 0 | New | Best shot: hook, value or give, soft ask | Interest / "want it?" |
| E2 | +3 | Reply | Short. **Written like a reply, not a reminder** (Instantly: about +30%), or delivers idea #2 | Permission |
| E3 | +7 | New or reply | **A different value lever** (if E1 saved time, E3 makes money) or a case study | Direct, or a "reply and it's yours" close |
| E4 | +14 | Reply | Breakup: wrong person / wrong timing / referral. **Skip for large lists** | Redirect |

- The 3-7-7 cadence captures about 93% of replies by day 10. Returns drop off after follow-up 2.
- Sources disagree on step count: Belkins says 2 emails, Instantly 4–7, lemlist up to 9. Our skills say 3–4. **With a TAM over 50k, send 1–2 emails and then pause 45+ days** (Nowoslawski).
- Don't repeat the same formula three times.

---

## 6. Personalization: what's safe in Bison

- **Every merge token must be bare, ALL-UPPERCASE, and registered.** `{VAR|fallback}` is spintax, not a fallback. c1127 delivered **0 real values of 308**, and c1109 shipped the literal word "personalization" to 305 people.
- `{FIRST_NAME}` is the only default token. Any other token goes in **its own full sentence on its own line**, so an empty value drops a line instead of breaking one.
- **Personalization depth is the biggest lever we have measured**: C1 with deep per-lead variables got 1.44% interested vs C2 with company plus first name at 0.23%, a **6x gap**. Hunter: 2 custom attributes lift replies from 3.6% to 5.6%.
- Batch-level AI failures: one prompt produces one skeleton for every lead, so rotate opening angles by a hash of the lead ID. Force second person. Review same-company leads side by side. **Never personalize on city or state** (the scraped geo data is unreliable).
- Signal fields: code establishes the facts and the model only rephrases them. An empty or "Unknown" value **removes the lead from the personalized branch**. Run 5 rows and read them before running 5,000.

---

## 7. Deliverability rules that shape wording

- **Spam words:** free, guarantee, act now, limited time, click here, buy now, discount, winner, urgent, 100%, risk-free. Say **"no cost"**, never "free".
- Run **mailmeteor-spam-check**. The target is **zero money/shady hits and a rating of Okay or better**. A single money or shady word scores 21+ points, an instant Poor. Don't contort natural phrasing just to reach Great.
- **Promise only what the sender controls:** no guarantees, no "we'll beat any quote".
- **Spintax:** greetings, transitions, CTAs, and sign-offs, with 3+ options each. Word-level only; never spin facts, names, numbers, or merge tags. Deliverability benefit **saturates at a few hundred combinations**. In Bison, **no spaces inside braces** (they render literally).
- **Opt-out:** our default is conversational ("If I'm barking up the wrong tree, let me know"). Gmail, Yahoo, and Outlook require one-click unsubscribe for *bulk* senders and a complaint rate under 0.3%. This is a deliberate trade-off. Consumer or regulated offers use the compliance-first variant.

---

## 8. Conflicts to decide

| # | Conflict | Sides | Recommendation |
|---|---|---|---|
| 1 | **P.P.C. direct call ask in E1** | pc-formula says "Let's do a call this week?" is earned; our data says a meeting ask halves positives, and **Bison activation blocks a meeting ask in step 1** | Use the soft P.P.C. close: "Want the other 3?" / "Want me to send it over?" |
| 2 | **Fake `Re:` on the first touch** | Jay kept it (the 22-campaign sample against it is thin); copy-constraints require non-deceptive subjects | **Don't use it on Consulti E1.** Real threading only |
| 3 | **"First name only" vs deep personalization** | The copywriting skill bans extra tokens; C1 vs C2 shows 6x from deep variables | Deep personalization, but only as **bare registered ALL-CAPS tokens on their own line**, or an AI specificity line |
| 4 | **Signal references in copy** | Banned for list campaigns; required in signal campaigns (Jay, 2026-08-19) | Decide the campaign type first |
| 5 | **Curiosity first line vs plain value** | Open-rate playbook: curiosity or confusion; 2026 Gemini summaries: state value plainly | Curiosity line 1, plain value line 2 |
| 6 | **Word count** | Our skills and Instantly say under 80; lemlist and Prosp say about 120 | Stay 50–90. P.E.C. is the only formula that justifies more than 100 |
| 7 | **Reply source** | Instantly: 58% of replies come from E1; Berman: follow-ups book 70–80% of meetings | Keep 3 steps and put the best copy in E1 |
| 8 | **Stale skill** | `cold-email` skill = an **old copy** of cold-email-copywriting ("prove you researched them" opener) | **Ignore `cold-email`**. Use `cold-email-copywriting` |

---

## 9. Benchmarks (set expectations honestly)

| Source | Reply rate |
|---|---|
| Smartlead H1 2026 (850M emails) | **median 0.74%**, top 10% 2.63% |
| Instantly 2026 (2025 data) | average 3.43%, top 10% 10.7%+ |
| Saleshandy H1 2026 | average 3.7% |
| Hunter 2026 | average 4.5%, sales use case 3% |
| Consulti own outbound (Jul 2026) | value-first **~0.38%**, ask-first ~0.15% |

Medians differ from averages, and self-serve accounts differ from agency-run ones. Smartlead's median is the most realistic reference point for high-volume sending.

**A/B testing reality check** (contacts **per arm** needed at 95% confidence / 80% power):

| Baseline | +50% lift | +25% lift |
|---|---|---|
| 0.25% | ~31,300 | ~112,700 |
| 0.50% | ~15,600 | ~56,200 |
| 1.00% | ~7,750 | ~27,900 |

At Consulti's ~0.4% baseline, the 17,820-contact master list **cannot tell apart 3–4 E1 wording variants**. Test only **big swings** (angle vs angle, or offer vs offer), split **at the campaign level** (one campaign per arm, disjoint senders, list split by a hash of the email). Use spintax for wording variety rather than treating wording as a test.

**Kit gates that affect this** (`lgj-cold-email-kit/.claude/rules/cold-email.md`):
- `bison campaigns activate` **refuses any step without an A/B split, step 1 above all**. Each campaign still needs at least 2 E1 variants, or `--accept-unsplit "<reason>"`. Keep the E1 variants within a campaign to frame-only changes (same offer, same CTA).
- **Don't compare reply rates across campaigns.** On 2026-08-20, 14 of 16 campaigns counted out-of-office messages as replies (`include_auto_replies_in_stats` is set per campaign). **Score on positive replies per 1,000 contacted.** The vendor reply-rate table above isn't comparable to our numbers.
- A merge field in the subject line came back 54–52 head to head, a coin flip. Subject character count showed no effect across 5,880 campaigns.
- Every connected sender needs a signature, or activation is blocked.
- **Opt-out depends on jurisdiction.** Australia's Spam Act requires a working unsubscribe on every commercial message, with no B2B carve-out. Decide per country before launch.

---

## 10. What this means for the new Consulti campaign

1. **Value-first is non-negotiable.** Open with the give: a sample list for their niche, or a gifted month of Pro. Say "no cost", never "free". Only the gifted month is free; the platform is paid.
2. **Default formula: Value Gift / soft P.P.C.** Hook, then "I pulled X for you", then "want it?".
3. **Untested angle worth an arm:** the MCP / AI-agent angle (drive Consulti from Claude, ChatGPT, or Cursor). It has never been tried, and it is a real differentiator.
4. **At most 2 campaign-level arms** (value-first control vs MCP angle), 3 steps, 3-7-7 cadence, no breakup step.
5. **Personalization:** add at least one real per-lead variable (for example their niche or audience noun) as a bare registered token on its own line, and verify 5 rendered rows before launch.
6. **Before launch:** run the dash lint, mailmeteor at Okay or better with zero money/shady hits, the Bison sequence lint, and `final-pre-launch`.

---

## Skill map: which skill to use when

| Need | Skill |
|---|---|
| ICP, offer, 3 angles | `cold-email-strategy` |
| Write the sequence (control copy) | `cold-email-copywriting` |
| Pain-first rewrite / choose P.C., P.E.C., or P.P.C. | `pc-formula` |
| Make an offer more irresistible | `hormozi-tips` |
| Variants + post-launch winner analysis | `cold-email-ab-testing` |
| Per-lead signal lines | `cold-email-signals` (+ `playbook-ai-specificity`) |
| Clay research + first-line prompts | `clay-personalization` |
| Spam-word score | `mailmeteor-spam-check` |
| Densify spintax on an existing campaign | `spintax-campaign-relaunch` |
| Jay's voice | `brand-voice` |
| Pre-launch QA | `final-pre-launch` |
| Not for cold email | `copywriting` (landing pages), `email-sequence` (IG nurture), `copy-editing` / `marketing-psychology` (generic), `cold-email` (stale duplicate) |

## Sources (web)
instantly.ai/cold-email-benchmark-report-2026 · smartlead.ai/benchmarks/average-cold-email-reply-rate · saleshandy.com/blog/cold-email-statistics · hunter.io/the-state-of-cold-email · belkins.io/blog/b2b-cold-email-subject-line-statistics · gong.io/blog/this-surprising-cold-email-cta-will-help-you-book-a-lot-more-meetings · clay.com/blog/b2b-cold-email-templates · alexberman.com/cold-email-ai-reply-rates-what-actually-works · prosp.ai/blog/ai-personalization-cold-outreach-what-works · lemlist.com/blog/cold-emailing · blog.google (Gmail Gemini era, Jan 2026) · mailgun.com (Microsoft sender requirements)
