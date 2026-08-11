---
name: apify-hiring-signals
description: >
  Turns LinkedIn job postings into actionable B2B sales intelligence by chaining
  three Apify Actors: (1) LinkedIn Jobs Scraper to find companies actively hiring
  for target roles, (2) Google Search Scraper to pull funding rounds, expansions,
  and growth signals for each company, and (3) Contact Info Scraper to surface
  decision-maker emails and phones from company websites.
  Use when asked to "find companies hiring [role]", "build a prospect list from
  job postings", "identify hiring signals", "generate leads from job boards",
  "which companies are investing in [department]", "find fast-growing companies
  in [industry]", "sales prospecting from LinkedIn", "map who's building a
  [team type] team", or "find companies that recently posted [job title] jobs".
metadata:
  category: data-extraction
  keywords: "hiring signals, lead generation, sales intelligence, linkedin jobs, b2b prospecting, contact enrichment, sales prospecting, job postings"
author: Khaled Ben Yahya
author_url: https://github.com/kingmathers92/
---

# Hiring Signals → Sales Intelligence

Convert LinkedIn job postings into a qualified B2B prospect list enriched with
growth signals and decision-maker contacts.

---

## Non-goals

- This skill does NOT perform general competitive intelligence
- This skill does NOT replace full market research tools
- This skill ONLY uses hiring signals to identify potential buyers

---

## Why Hiring Signals?

Job postings are the strongest buying signal in B2B sales. A company posting
5 "Senior Data Engineer" roles is almost certainly evaluating data tooling.
A company hiring 10 "Account Executive" roles is scaling revenue and likely
needs sales tech. This skill surfaces those signals before your competitors do.

## Prerequisites

_(No need to check upfront — handle errors inline if they arise)_

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

Copy this checklist and track progress as you go:

```
Task Progress:
- [ ] Step 1: Clarify target (role, location, industry filters)
- [ ] Step 2: Scrape LinkedIn jobs → extract company list
- [ ] Step 3: Enrich companies with Google news signals
- [ ] Step 4: Extract decision-maker contacts from company websites
- [ ] Step 5: Synthesize and deliver prospect table
```

---

### Step 1: Clarify the Target Signal

Ask the user (or infer from their message) for:

| Parameter                          | Example                                            |
| ---------------------------------- | -------------------------------------------------- |
| **Target job title(s)**            | "Data Engineer", "VP of Sales", "Head of Security" |
| **Location filter**                | "United States", "London", "Remote"                |
| **Industry filter** _(optional)_   | "SaaS", "Fintech", "Healthcare"                    |
| **Company size hint** _(optional)_ | "startups", "Series B+", "enterprise"              |
| **Max companies to return**        | Default: 20, warn before 50+                       |

**Shortcut**: For simple queries like "find 10 SaaS companies hiring data engineers in NYC", skip asking and proceed directly.

---

### Step 2: Scrape LinkedIn Jobs

**Actor**: `curious_coder/linkedin-jobs-scraper`

First, fetch the input schema so you build the input correctly:

```bash
apify actors info "curious_coder/linkedin-jobs-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null
```

Then run the scraper:

```bash
apify actors call "curious_coder/linkedin-jobs-scraper" \
  -i '{"keywords": "JOB_TITLE", "location": "LOCATION", "limitPerSource": MAX_RESULTS, "scrapeCompany": true}' \
  --json \
  --user-agent apify-awesome-skills/apify-hiring-signals \
  2>/dev/null
```

Fetch the results from the run's dataset:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null
```

**Extract from results**:

- company name → deduplicate into a unique company list
- company LinkedIn URL or website URL → use as enrichment seed
- job title, posted date → keep for context
- company size → filter if user asked for size

**Fallback** — if LinkedIn returns 0 results (rate-limited or geo-blocked):

```bash
apify actors call "apify/google-search-scraper" \
  -i '{"queries": "site:linkedin.com/jobs JOB_TITLE LOCATION", "maxPagesPerQuery": 3}' \
  --json \
  --user-agent apify-awesome-skills/apify-hiring-signals \
  2>/dev/null
```

`maxPagesPerQuery` is the only result-count control on this Actor's input
schema (there is no `resultsPerPage` field) — each page returns roughly 10
results, so `maxPagesPerQuery: 3` yields up to ~30 results.

Parse company names and URLs from the Google SERP titles and snippets.

---

### Step 3: Enrich with Google News Signals

We batch company enrichment queries to minimize cost and reduce API calls.

For each unique company from Step 2, run **one batched Google Search** to pull
funding rounds, expansions, product launches, and leadership changes.

**Actor**: `apify/google-search-scraper`

Build a newline-separated query list where each line is a company-specific
signal query:

```bash
apify actors call "apify/google-search-scraper" \
  -i '{"queries": "\"COMPANY_1\" funding OR raises OR expansion OR launch 2024 OR 2025\n\"COMPANY_2\" funding OR raises OR expansion OR launch 2024 OR 2025", "maxPagesPerQuery": 1, "countryCode": "us"}' \
  --json \
  --user-agent apify-awesome-skills/apify-hiring-signals \
  2>/dev/null
```

**Cost control**: batch all company queries in a single Actor run (pass the
full newline-separated `queries` string). Do NOT run one Actor call per company.

**Extract per company**:

- Latest funding round + amount (if mentioned)
- Recent product or expansion news
- Key executive names from bylines

---

### Step 4: Extract Decision-Maker Contacts

For each company website URL gathered in Step 2, run the Contact Info Scraper
to find emails and phone numbers — especially on `/about`, `/team`, `/contact` pages.

**Actor**: `vdrmota/contact-info-scraper`

```bash
apify actors call "vdrmota/contact-info-scraper" \
  -i '{"startUrls": [{"url": "https://COMPANY_1_WEBSITE/contact"}, {"url": "https://COMPANY_2_WEBSITE/about"}], "maxDepth": 1, "maxRequestsPerStartUrl": 3, "sameDomain": true}' \
  --json \
  --user-agent apify-awesome-skills/apify-hiring-signals \
  2>/dev/null
```

**Extract**:

- `emails` array → filter out support@, info@, noreply@ — keep personal or
  role-based addresses (e.g. cto@, vp-sales@, firstname.lastname@)
- `phones` array → keep if present
- `linkedIns` → executive profile links if present

**Skip this step** for quick/overview queries where the user only asked for a
company list, not contact details.

---

### Step 5: Synthesize and Deliver

Assemble a prospect table sorted by signal strength (most recent funding or
highest job-posting volume first):

```
| Company | Role Posted | # Jobs | Latest Signal | Contact |
|---------|-------------|--------|---------------|---------|
| Acme Corp | Head of Data | 4 | Series B ($12M, Jan 2025) | cto@acme.com |
| Beta Inc | VP of Sales | 2 | Expansion to EU (Mar 2025) | — |
```

Always include:

- **Total companies found** and **after deduplication**
- **Actors used** and approximate credit cost
- **Suggested follow-up**: "Want me to export this as a CSV?" or "Should I
  search for the direct LinkedIn profiles of the decision-makers?"

For CSV output, fetch the dataset as JSON and convert it (e.g. with `jq` or a
spreadsheet tool):

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-hiring-signals \
  2>/dev/null > YYYY-MM-DD_prospects.json
```

---

## Output Formats

| Format              | When to use              | How                                                 |
| ------------------- | ------------------------ | --------------------------------------------------- |
| Quick table in chat | ≤ 20 companies, overview | _(default — assemble from JSON results)_            |
| CSV                 | Full export, CRM import  | Fetch dataset as JSON, convert with `jq` or similar |
| JSON                | Downstream automation    | `apify datasets get-items DATASET_ID --format json` |

---

## Cost Safety

Always cap results before running:

| Actor                                 | Field to cap             | Default cap |
| ------------------------------------- | ------------------------ | ----------- |
| `curious_coder/linkedin-jobs-scraper` | `limitPerSource`         | 50          |
| `apify/google-search-scraper`         | `maxPagesPerQuery`       | 1           |
| `vdrmota/contact-info-scraper`        | `maxRequestsPerStartUrl` | 3           |

Warn the user before running more than 50 companies through the full 3-actor
pipeline — that can consume significant credits.

---

## Error Handling

| Error                     | Cause                       | Fix                                              |
| ------------------------- | --------------------------- | ------------------------------------------------ |
| `Not authenticated`       | Missing Apify auth          | Run `apify login` or set `APIFY_TOKEN`           |
| `Actor not found`         | Typo in Actor ID            | Verify spelling; re-run `apify actors info`      |
| `Run FAILED`              | Auth, quota, or input error | Check Apify console link in error output         |
| `0 results from LinkedIn` | Rate-limited                | Use Google fallback in Step 2                    |
| `contacts array empty`    | No public emails on site    | Note in output; suggest LinkedIn manual lookup   |
| `Timeout`                 | Too many URLs in batch      | Reduce `startUrls` to ≤ 10 per run               |
