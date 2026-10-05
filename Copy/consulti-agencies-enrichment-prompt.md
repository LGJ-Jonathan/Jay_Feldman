# Consulti Agencies - Give-First 2 - CLIENT_NICHE Enrichment (Clay)

Fills `{CLIENT_NICHE}` for every lead in `consulti-agencies-give-first-2.md`.
`{COMPANY}` and `{COWORKER_NAME_2}` are already filled.

## Why separate steps
1. **Company research (Claygent, web access):** reads the website and writes down facts. Expensive, so it runs once.
2. **Client niche (plain AI column, no web):** turns those facts into one clean value that fits the copy. Cheap, so you can re-run it if you change the rules without paying for research again.

Running both in one prompt works, but when a niche comes out wrong you can't tell if the research missed it or the formatting rule broke, and every fix re-pays for the web research.

## Clay columns
| # | Column | Type | Input |
|---|---|---|---|
| 1 | `linkedin_headline` | Enrich Person from LinkedIn URL (optional) | person LinkedIn URL |
| 2 | `company_description` | Claygent with web access, single text output | Prompt 1 |
| 3 | `qualified` | AI column, single text output (yes/no), no web | Prompt 2 |
| 4 | `CLIENT_NICHE` | AI column, single text output, no web, only runs when `qualified` = yes | Prompt 3 |

Map `CLIENT_NICHE` to the Bison custom variable `CLIENT_NICHE` exactly.

---

## Prompt 1: company research (Claygent)

Output: ONE text column, `company_description`.
Clay builds an output field for every numbered item or label it sees, so this prompt is written as plain sentences on purpose. In the Claygent setup, open **Outputs**, delete every field except one, name it `company_description`, type Text. If "JSON / structured output" is on, turn it off.

```
Visit {{Website}} and read the homepage plus any About, Services, Industries, Who We Serve, Case Studies, Portfolio or Clients pages. The company is {{Company Name}}. The contact's LinkedIn headline, which may be empty, is: {{linkedin_headline}}

Write a single paragraph of 4 to 6 sentences describing this company, and return only that paragraph as one text value. Do not use bullet points, numbers, headings, labels, JSON or line breaks.

In the paragraph, say what services they sell and what kind of company they are, such as a marketing agency, advertising agency, fractional CMO or consultant, PR firm, printing or promo products company, software company, or in-house marketing team. Say what type of businesses their clients are, quoting their own phrase if they have one, such as "marketing for dental practices". Mention any industry pages and the industries of the case studies or clients shown, with rough counts. Only mention a city or region if the site says they focus on businesses there, and quote it; an address alone does not count. End by saying whether the company appears active, or whether the site shows it closed, was acquired or merged, the owner retired, or the website is parked or broken.

Only write what the website or headline actually says. If something is not stated, say so in the sentence. Do not guess.
```

---

## Prompt 2: pre-qualify (AI column)

Output: ONE text column, `qualified`, value `yes` or `no`. Single Text output, JSON off. Run Prompt 3 only on rows where `qualified` = yes (set it as the run condition, or filter first).

```
Read this description of {{Company Name}} and decide if the company is a fit for our offer.

{{company_description}}

Our offer is a no-cost list of verified contacts that a marketing agency or marketing consultant can use to win new clients or run campaigns for their clients. A fit is a company that sells marketing services to other businesses.

Answer yes if the company is a marketing agency, digital marketing agency, advertising agency, SEO, PPC, paid ads, social media, web design, branding, content or email marketing agency, lead generation or appointment setting agency, fractional CMO, marketing or growth consultant, or an AI automation agency that does marketing or sales work for clients.

Answer no if any of these are true: the company mainly does public relations, billboards or outdoor advertising, printing, promotional products or merchandise; it sells its own software, app or platform; it is a market research, clinical research, insurance, financial, legal, staffing, recruiting, real estate, IT services or general tech consulting company; it is a nonprofit, school or government body; it is a brand, store or manufacturer marketing its own products; it is not a business that serves clients; the description says it closed, was acquired or merged, or the owner retired; or the website is parked, broken or gives too little information to tell.

If it does several things, judge by what it mainly sells. If you are unsure, answer no.

Return only the word yes or no, in lowercase, with nothing else.
```

---

## Prompt 3: client niche (AI column)

Output: ONE text column, `CLIENT_NICHE`. Single Text output, JSON off. Run condition: `qualified` = yes.

```
Read this description of {{Company Name}}, a marketing agency or consultant, and decide what type of businesses their clients are.

{{company_description}}

Your answer is inserted into a cold email to the owner of this company, offering them a no-cost list of contacts at businesses in their niche. It must read naturally in all of these lines:

{CLIENT_NICHE} list
list of {CLIENT_NICHE} for {{Company Name}}
I can pull 300 verified contacts at {CLIENT_NICHE} for {{Company Name}}, on us.
In case it's useful, here's what's in the {CLIENT_NICHE} list.
Last note from me. The {CLIENT_NICHE} list is still yours.

Always return exactly one value from the approved list below, copied exactly, including capital letters. Never invent a new value, never return a blank, never add quotes, punctuation or explanation.

Approved industry values: dental practices, medical practices, healthcare companies, med spas, chiropractors, law firms, home service companies, HVAC companies, plumbing companies, roofing companies, construction companies, real estate agencies, restaurants, hospitality businesses, fitness studios, salons and spas, veterinary clinics, auto dealerships, insurance agencies, financial advisors, accounting firms, professional services firms, manufacturers, ecommerce brands, SaaS companies, tech companies, B2B companies, education companies, nonprofits

Approved city values, written as the city followed by businesses: New York businesses, Los Angeles businesses, Chicago businesses, Dallas businesses, Houston businesses, Washington DC businesses, Philadelphia businesses, Miami businesses, Atlanta businesses, Boston businesses, Phoenix businesses, San Francisco businesses, Seattle businesses, Detroit businesses, Minneapolis businesses, San Diego businesses, Tampa businesses, Denver businesses, Baltimore businesses, St. Louis businesses, Orlando businesses, Charlotte businesses, San Antonio businesses, Austin businesses, Portland businesses, Sacramento businesses, Pittsburgh businesses, Las Vegas businesses, Cincinnati businesses, Kansas City businesses, Columbus businesses, Indianapolis businesses, Cleveland businesses, San Jose businesses, Nashville businesses, Jacksonville businesses, Raleigh businesses, Salt Lake City businesses

Approved general values: local businesses, small businesses

How to choose:

First, look for an industry. Pick an industry value if the description says they serve one industry, or names one industry as their specialty, or at least half of their industry pages or case studies are in one industry. Map close matches to the nearest approved value: dentists and orthodontists become dental practices; doctors, clinics and hospitals become medical practices or healthcare companies; attorneys become law firms; contractors, landscapers, pest control, cleaning and other trades become home service companies; hotels and travel become hospitality businesses; gyms become fitness studios; software, apps and tech startups become SaaS companies or tech companies; consultants, agencies and other service firms become professional services firms; online stores and DTC brands become ecommerce brands; schools and course creators become education companies. If two or more industries are equally strong, do not pick one, move on.

Second, if there is no clear industry, look for a city focus. Pick a city value only if the description says they focus on serving businesses in that city or its metro area, not just that their office is there. A suburb counts as its metro, so Scottsdale is Phoenix businesses and Fort Lauderdale is Miami businesses. If the city is not on the approved list, skip this step.

Third, if neither applies, return local businesses when the description says they serve local or brick and mortar businesses in their community, otherwise return small businesses.

When unsure between two choices, take the later, more general one. A wrong niche hurts more than a general one.

Return only the value.
```

---

## Prompt 3B: single-prompt client niche, less generic (Claygent with web access)

Replaces Prompt 1 + Prompt 3 in one column. Output: ONE text column, `CLIENT_NICHE`. Single Text output, JSON off. Run condition: `qualified` = yes (or, to save credits, only on rows where the old niche is small businesses, local businesses or B2B companies).

```
You are finding the client niche of {{Company Name}}, a marketing agency or consultant. Their website is {{Website}}. Their LinkedIn description, which may be empty, is: {{company_description}}

Visit the website. Read the homepage, About, Services and Industries pages, and then look for real clients: Portfolio, Work, Case Studies, Clients, Testimonials, Reviews and client logos. Note the name and industry of every client you can identify, up to 10. Also note the city and state of their office from the footer or contact page.

Your answer is inserted into a cold email to the owner of this company, offering them a no-cost list of contacts at businesses in their niche. It must read naturally in all of these lines:

{CLIENT_NICHE} list
list of {CLIENT_NICHE} for {{Company Name}}
I can pull 300 verified contacts at {CLIENT_NICHE} for {{Company Name}}, on us.
In case it's useful, here's what's in the {CLIENT_NICHE} list.
Last note from me. The {CLIENT_NICHE} list is still yours.

Return exactly one value from the approved lists below, copied exactly, including capital letters. Never invent a value, never return a blank, never add quotes, punctuation or explanation.

Approved industry values: dental practices, medical practices, healthcare companies, med spas, chiropractors, law firms, home service companies, HVAC companies, plumbing companies, roofing companies, construction companies, real estate agencies, restaurants, hospitality businesses, fitness studios, salons and spas, veterinary clinics, auto dealerships, insurance agencies, financial advisors, accounting firms, professional services firms, manufacturers, ecommerce brands, SaaS companies, tech companies, B2B companies, education companies, nonprofits

Approved city values: New York businesses, Los Angeles businesses, Chicago businesses, Dallas businesses, Houston businesses, Washington DC businesses, Philadelphia businesses, Miami businesses, Atlanta businesses, Boston businesses, Phoenix businesses, San Francisco businesses, Seattle businesses, Detroit businesses, Minneapolis businesses, San Diego businesses, Tampa businesses, Denver businesses, Baltimore businesses, St. Louis businesses, Orlando businesses, Charlotte businesses, San Antonio businesses, Austin businesses, Portland businesses, Sacramento businesses, Pittsburgh businesses, Las Vegas businesses, Cincinnati businesses, Kansas City businesses, Columbus businesses, Indianapolis businesses, Cleveland businesses, San Jose businesses, Nashville businesses, Jacksonville businesses, Raleigh businesses, Salt Lake City businesses

Approved state values: the full US state name followed by businesses, for example Ohio businesses, North Carolina businesses, Texas businesses

Approved general value: small businesses

How to choose, in this order:

First, industry. Pick an industry value if the site says they specialize in one industry, or has one main industry page, or at least 3 of the clients you identified are in the same industry, or one industry clearly has more clients than any other. Map close matches to the nearest approved value: dentists and orthodontists become dental practices; doctors, clinics and hospitals become medical practices or healthcare companies; attorneys become law firms; contractors, landscapers, pest control, cleaning and other trades become home service companies; hotels and travel become hospitality businesses; gyms become fitness studios; online stores and DTC brands become ecommerce brands; schools and course creators become education companies. If the clients are B2B, return the most specific type shown: SaaS companies, tech companies, manufacturers, professional services firms, or financial advisors. Only return B2B companies if none of these fit. If two industries are tied, move on.

Second, location. If there is no clear industry but the agency serves local businesses, or most identified clients are in the same area as its office, use its office location. If the office is in or near a city on the approved city list, return that city value; a suburb counts as its metro, so Scottsdale is Phoenix businesses. Otherwise return the state value for the office state. Only use a US location.

Third, if nothing above applies, return small businesses.

A wrong niche is worse than a general one, so only pick an industry or location you can support with what is on the website.

Return only the value.
```

---

## Spot check (run 50 rows first)
- Read "300 verified contacts at {CLIENT_NICHE}" for 10 rows. Nothing awkward?
- `generic` above ~60%: Claygent is probably failing to load sites. Check a few `company_description` cells.
- Every value is on the approved list (no blanks, no invented values).
- Count distinct `CLIENT_NICHE` values. Each one needs a prebuilt 300-contact list, so merge near-duplicates into the canonical list.
