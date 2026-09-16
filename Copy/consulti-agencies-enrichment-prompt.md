# Consulti Agencies - Give-First 2 - Enrichment Prompt

Fills the variables for the two Email 1 variants in `consulti-agencies-give-first-2.md`.
Run once per lead, after the GetLeads export and the suppression/dedupe step.

## Setup in Clay
1. **Input columns** (from the GetLeads export): `first_name`, `job_title`, `linkedin_headline`, `company_name`, `company_domain`, `company_description`, `city`, `state`, `employees`
2. **Website column:** "Scrape Website" (or Claygent with web access) on `company_domain`, homepage + /about + /services, text only
3. **AI column:** paste the prompt below, output as JSON, map each key to its own column
4. **Filter after:** `qualified = yes`, then send `list_key` to the fulfillment automation

---

## Prompt

```
You are qualifying a marketing agency or consultant for a cold email and filling the variables that personalize it.

INPUTS
Company: {{company_name}}
Domain: {{company_domain}}
Location: {{city}}, {{state}}
Employees: {{employees}}
Contact title: {{job_title}}
Contact headline: {{linkedin_headline}}
LinkedIn About: {{company_description}}
Website text: {{website_text}}

The email will say:
  Subject: "{CLIENT_NICHE} list"
  "saw {COMPANY} does {SERVICE} for {CLIENT_NICHE}."
  "sourcing a clean list of {CLIENT_NICHE} eats a few hours every time."
  "I can pull you 300 verified contacts at {CLIENT_NICHE}"
Every value you return must read naturally in ALL of those sentences.

Return ONLY this JSON:
{
  "client_niche": "",
  "niche_type": "",
  "service": "",
  "segment": "",
  "qualified": "",
  "disqualify_reason": "",
  "list_key": "",
  "evidence": ""
}

RULES

1. client_niche: who this company's CLIENTS are.
   Pick using these tiers, in order:

   a) INDUSTRY. The website or About clearly says they focus on one type of business
      (a niche page, "we work with...", "marketing for...", most case studies in one industry).
      Use the closest value from this list, exactly as written:
        dental practices, medical practices, med spas, chiropractors, law firms,
        home service companies, HVAC companies, plumbing companies, roofing companies,
        construction companies, real estate agencies, restaurants, hotels,
        auto dealerships, fitness studios, salons and spas, veterinary clinics,
        insurance agencies, financial advisors, accounting firms, manufacturers,
        ecommerce brands, SaaS companies, B2B companies, nonprofits
      If they focus on one industry that is not on the list, write it the same way:
      plural, lowercase, the name of a BUSINESS not a person
      ("law firms" not "lawyers", "dental practices" not "dentists").
      Never a consumer group ("homeowners", "patients", "moms").
      Maximum 3 words.
      niche_type = "industry"

   b) GEO. No single industry, but they clearly market to businesses in one city or metro
      ("Jacksonville's marketing agency", "helping Denver businesses grow").
      Format exactly: "<City> businesses" (e.g. "Jacksonville businesses").
      Use the city named on the site, not just the HQ address.
      niche_type = "geo"

   c) GENERIC. Anything else, or you are not sure.
      client_niche = "small businesses"
      niche_type = "generic"

   Several industries listed equally = GENERIC (or GEO if a city focus is clear).
   Do not guess from one case study.

2. service: their main service, as it would finish "does ___ for".
   Use one of: SEO, PPC, paid ads, social media marketing, web design, branding,
   content marketing, email marketing, video production, lead generation,
   marketing strategy, AI automation, marketing
   Keep acronyms uppercase (SEO, PPC, AI). Everything else lowercase.
   Full-service agency or several equal services = "marketing".
   Fractional CMO or strategy consultant = "marketing strategy".

3. segment:
   "consultant" = fractional CMO, solo or small consultant, advisor, AI automation consultant,
                  or the contact's title/headline says fractional, consultant, or advisor.
   "agency"     = an agency with a team that delivers marketing services for clients.
   If both could apply, choose "consultant".

4. qualified = "no" if ANY of these are true, otherwise "yes":
   - Website missing, parked, for sale, or has no real content
   - Site says the company closed, was acquired, merged, or the owner retired
   - Mainly PR / public relations, billboards / outdoor, printing, or promo products
   - Staffing, recruiting, real estate brokerage, or software/SaaS product company
   - An in-house marketing team (they market their own company, not clients)
   - The contact is not an owner, founder, partner, principal, president, or CEO
   Put a short reason in disqualify_reason. Leave it "" when qualified = "yes".

5. list_key: the key the fulfillment automation uses to pick the prebuilt list.
   industry -> "industry:<client_niche>"   e.g. "industry:dental practices"
   geo      -> "geo:<City>, <ST>"           e.g. "geo:Jacksonville, FL"
   generic  -> "generic:small businesses"

6. evidence: under 20 words quoting or paraphrasing what on the site decided client_niche.

Never invent facts. If the website text is empty, use the LinkedIn About.
If both are empty: qualified = "no", disqualify_reason = "no website or description".
```

---

## Spot check before running the full list
Run 50 rows first and check:
- Read the first line out loud for 10 rows: "saw {COMPANY} does {SERVICE} for {CLIENT_NICHE}." Nothing awkward?
- `generic` share. If it is above ~60%, the geo tier is too strict or the website scrape is failing.
- Every `qualified = no` reason looks right (no good agencies thrown out).
- No consumer groups or person nouns slipped into `client_niche`.
