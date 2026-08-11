<a href="https://skills.sh/apify/awesome-skills"><img src="https://skills.sh/b/apify/awesome-skills" alt="skills.sh installs"></a>

<p align="center">
  <img src="https://docs.apify.com/img/apify_logo.svg" alt="Apify" width="96" height="96">
</p>

<h1 align="center">Awesome Apify Skills</h1>

<p align="center">
  <strong>Community-driven agent skills for AI coding assistants</strong>
</p>

<p align="center">
  <a href="https://apify.com"><img src="https://img.shields.io/badge/Powered%20by-Apify-20A34E?style=for-the-badge" alt="Powered by Apify"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache--2.0-555555?style=for-the-badge" alt="Apache 2.0"></a>
  <a href="#bounty"><img src="https://img.shields.io/badge/Bounty-%24100%2FPR-F86606?style=for-the-badge" alt="$100/PR bounty open"></a>
  <a href="#available-skills"><img src="https://img.shields.io/badge/Skills-8-246DFF?style=for-the-badge" alt="8 Skills"></a>
  <a href="https://apify.com/store"><img src="https://img.shields.io/badge/Actors-30%2C000%2B-F86606?style=for-the-badge" alt="30,000+ Actors"></a>
  <a href="https://github.com/apify/awesome-skills/stargazers"><img src="https://img.shields.io/github/stars/apify/awesome-skills?style=for-the-badge&color=9D97F4&label=Stars" alt="GitHub stars"></a>
</p>

<p align="center">
  <a href="#install">Quick start</a> &bull;
  <a href="#available-skills">Skills</a> &bull;
  <a href="#contribute">Contribute</a> &bull;
  <a href="#bounty">Bounty</a> &bull;
  <a href="#for-ai-agents">For AI agents</a> &bull;
  <a href="#support">Support</a>
</p>

Companion to [apify/agent-skills](https://github.com/apify/agent-skills), the home of official Apify-maintained skills. This repo collects community contributions that follow the same [agentskills.io](https://agentskills.io/specification) open standard.

<a id="bounty"></a>

> [!IMPORTANT]
> ### 🎁 Community bounty open
>
> Get **$100 in Apify credits** for every merged PR that adds a new creative skill to this repo.
>
> - One per contributor
> - First 10 merged PRs only
> - Closes **June 30, 2026** or after the 10th merge, whichever comes first
>
> [How to submit →](CONTRIBUTING.md)

## What's a skill?

A skill is a `SKILL.md` file with YAML frontmatter that teaches an AI agent how to do a specific task with [Apify Actors](https://apify.com/store) — which Actors to use, how to build inputs, how to handle errors.

## Install

```bash
npx skills add apify/awesome-skills
```

Works with Claude Code, Codex, Cursor, Gemini CLI, Windsurf, OpenCode, and [50+ other agents](https://skills.sh). Pass `--list` to preview, `-s <name>` to install one specific skill.

## Available skills

<!-- BEGIN_SKILLS_TABLE -->
| Name | Description | Author |
|------|-------------|--------|
| [`apify-ads-intelligence`](skills/apify-ads-intelligence/SKILL.md) | Research, spy on, and analyze ads across Meta (Facebook & Instagram), Google (Ads Transparency Center + paid search results), TikTok (Ads Library + Creative Center), LinkedIn Ad Library, and X (Twitter — promoted tweets, best-effort) using Apify Actors. Use when user asks about competitor ads, ad library research, winning creatives, ad copy analysis, landing page audits from ads, cross-platform ad audits, brand transparency checks, or any task involving paid ad creatives, advertiser data, or ad targeting from public ad libraries. | [Sameh Jarour](https://github.com/samehjarour) |
| [`apify-ai-search-visibility-tracker`](skills/apify-ai-search-visibility-tracker/SKILL.md) | Track whether a brand and its competitors get cited or mentioned across Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, and Google Gemini for a defined set of prompts, on a recurring schedule. Use when user asks to track AI visibility, monitor brand mentions in AI search, track ChatGPT citations, do AI search SEO tracking, GEO tracking (Generative Engine Optimization), AEO tracking (Answer Engine Optimization), monitor Perplexity citations, track AI Overviews mentions, see if their brand shows up in AI search, discover which prompts competitors rank for in AI search, find citation opportunities, or audit a website for AI visibility readiness. | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-app-store-intelligence`](skills/apify-app-store-intelligence/SKILL.md) | App-store intelligence and ASO research across the Apple App Store, Google Play, and the Shopify App Store. Pull app details, exact ratings and ratings histograms, customer reviews, and keyword/category rankings, then compare an app against its competitors. Use when the user asks to scrape App Store or Google Play data, track app reviews or ratings over time, do ASO / app-store keyword rank research, monitor competitor apps, mine app reviews for sentiment or feature requests, or research the Shopify app ecosystem. Requires the Apify CLI or the Apify MCP server. | [FreshActors](https://github.com/Freshactors) |
| [`apify-booking-host-leads`](skills/apify-booking-host-leads/SKILL.md) | Find and enrich B2B leads from Booking.com - hotels, apartments, and vacation rentals - and pull each host's or property manager's real contact details (email, phone, company name, registration number). Use when the user says things like "get emails from Booking.com", "Booking.com lead generation", "find tour operator / property manager / host contacts", "scrape accommodation owner emails", or "build a list of Booking hosts". The host's email is usually already inside the Booking scraper's traderInfo field (EU/AU trader-transparency disclosure) - this skill leads with that and uses a Google Maps email scraper only as a fallback, instead of relying on Google Maps first (which mostly returns the wrong business). | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-bounty-radar`](skills/apify-bounty-radar/SKILL.md) | Find, screen, and prioritize public GitHub bounty opportunities with Apify Actors. Use when a user asks to find paid GitHub issues, Algora or Polar bounties, bounty races, claimable open-source tasks, or recently posted contribution opportunities, and needs evidence on payout terms, competition, assignment rules, and claimability before starting work. | [Peter7896](https://github.com/Peter7896) |
| [`apify-easy-competitive-intelligence`](skills/apify-easy-competitive-intelligence/SKILL.md) | This skill should be used when the user asks to "analyze a competitor", "compare pricing", "competitive landscape", "market research", "what do customers think", "review intelligence", "hiring signals", "content strategy", "SEO battle", "build a battlecard", "competitive analysis", "who are the players", "who competes with", "market intelligence", "competitive positioning", "deep dive on a company", "board prep", "SWOT analysis", "how does [X] compare to [Y]", or mentions competitor analysis, pricing comparison, customer sentiment, or market landscape research. Requires Apify CLI or Apify MCP server. | [chocholous](https://github.com/chocholous) |
| [`apify-ecommerce`](skills/apify-ecommerce/SKILL.md) | Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence. | [Luis Pinto](https://github.com/luispintoapify) |
| [`apify-financial-services`](skills/apify-financial-services/) | Financial company intelligence — news monitoring (33 sources), social listening (Reddit, Twitter/X, Trustpilot), and public registry lookups (11 European countries). 3 skills + portfolio-sweep command. | — |
| [`apify-hiring-signals`](skills/apify-hiring-signals/SKILL.md) | Turns LinkedIn job postings into actionable B2B sales intelligence by chaining three Apify Actors: (1) LinkedIn Jobs Scraper to find companies actively hiring for target roles, (2) Google Search Scraper to pull funding rounds, expansions, and growth signals for each company, and (3) Contact Info Scraper to surface decision-maker emails and phones from company websites. Use when asked to "find companies hiring [role]", "build a prospect list from job postings", "identify hiring signals", "generate leads from job boards", "which companies are investing in [department]", "find fast-growing companies in [industry]", "sales prospecting from LinkedIn", "map who's building a [team type] team", or "find companies that recently posted [job title] jobs". | [Khaled Ben Yahya](https://github.com/kingmathers92/) |
| [`apify-influencer-brand-collabs`](skills/apify-influencer-brand-collabs/SKILL.md) | Discover Instagram brand–creator partnerships by chaining Apify Actors. Use when the user asks who collabs with a brand, which brands a creator has done paid posts for, wants to audit an influencer's branded-content history, or wants to scope a brand's sponsorship roster. **Triggers:** - "who collabs with [brand] on Instagram?" - "what brands has [creator] done sponsored posts for?" - "find paid partnerships / branded content for [handle]" - "audit [influencer]'s brand deals" - "show me [brand]'s influencer roster" Works in either direction — brand → creators or creator → brands — and detects direction from the data, so don't ask the user to declare it. Requires Apify MCP tools. | [Natasha Lekh](https://github.com/natashalekh) |
| [`apify-job-market-intelligence`](skills/apify-job-market-intelligence/SKILL.md) | Build job-market intelligence from public job boards using Apify Actors. Use when the user asks to analyze hiring demand, find companies hiring for a role, compare job-market trends, scrape LinkedIn Jobs, Google Jobs, Indeed, or Glassdoor, extract required skills from postings, rank target companies, benchmark salaries, or create a focused job-search pipeline. | [Samyak Jain](https://github.com/Samyak-jain7) |
| [`apify-jobs-data`](skills/apify-jobs-data/SKILL.md) | Extract clean, de-noised job-posting data from LinkedIn, Indeed, Glassdoor, Google Jobs, and 20+ boards in one Apify run — deduplicated across boards with ghost jobs and reposts removed and fields normalized — then analyze it (deduped hiring demand, in-demand skills, coverage-labeled salary distribution), export it (CSV / JSON / Apify dataset) for dashboards and BI, or rank it against a résumé. Use when the user asks to scrape job postings, build a job dataset, analyze hiring demand or in-demand skills or salary ranges for a role or market, export job data for a dashboard or spreadsheet, dedupe job listings across boards, filter out ghost or fake jobs, or rank jobs by fit to a résumé. Triggers - "scrape job postings for X", "what skills are in demand for Y", "salary range for Z in [location]", "export job data to CSV", "filter out the ghost jobs", "which of these jobs fit my résumé". | [Oleg Martinez](https://github.com/ezumyn-aliegm) |
| [`apify-link-prospecting-outreach`](skills/apify-link-prospecting-outreach/SKILL.md) | Find sites ranking for target keywords, score every prospect with Ahrefs domain authority and page-level traffic, identify the strongest pitch angle per row ("links to competitor", "mentions brand without linking", "top-3 SERP", "resource page", "outdated content"), generate brand-voice-matched outreach emails using an outreach-type-aware template (unlinked-mention claim, competitor-link replacement, resource-page inclusion, outdated-content replacement, topical niche-edit), and propose a concrete in-article link placement as three artifacts — the verbatim source sentence, the same sentence rewritten with the link spliced in, or a fully-drafted new insertion if no natural fit exists. Use when user asks to find link building opportunities, prospect link partners, recover unlinked brand mentions, replace competitor links, build a tiered outreach list, or run cold email outreach for SEO link building. | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-reddit-research`](skills/apify-reddit-research/SKILL.md) | Research discussions, sentiment, opinions, and trends on Reddit. Use when the user asks what Reddit thinks about a topic/brand/product/company, wants subreddit analysis, needs to find real conversations, monitor brand mentions, analyze customer sentiment, research trends, or gather Reddit data for competitive intelligence and market research. Supports keyword search, specific subreddits, user profiles, and post URLs. | [Jose Gabriel Rivera](https://github.com/grivera82) |
| [`apify-sec-regulatory-intelligence`](skills/apify-sec-regulatory-intelligence/SKILL.md) | Monitor and extract U.S. SEC and global financial-regulator filings via Apify Actors. Use to track insider trades (Form 4), material corporate events (8-K), institutional 13F holdings and changes, activist stakes (13D/G), private placements (Form D / Reg A+), late-filing warnings (Form NT), fund holdings & proxy votes (N-PORT / N-PX), investment advisers (Form ADV), restricted-stock pre-sales (Form 144), SEC litigation & enforcement, FINRA BrokerCheck, or enforcement from global regulators (Swiss FINMA, Singapore MAS, Hong Kong SFC, India SEBI, Australia ASIC, Japan EDINET, China A-share, UK RNS). Triggers - "track insider buying", "who's buying/selling [ticker]", "recent 8-K events", "13F changes for [fund]", "activist 13D filings", "new Form D raises", "SEC enforcement this year", "check a broker on FINRA", "companies that filed late", "regulatory enforcement in [country]", "SEC filings for [company]". Factual public filing data for research - not financial, legal, or investment advice. | [NexGenData](https://apify.com/nexgendata) |
| [`apify-sim-bravo`](skills/apify-sim-bravo/SKILL.md) | Simulation skill Bravo. Second half of the parallel-merge scenario — merged immediately after Alpha from an independent branch, without rebase and without touching the generated catalog. Not a real skill; safe to delete. | [sim-harness](https://github.com/chocholous/awesome-skills-sim) |
| [`apify-social-listening`](skills/apify-social-listening/SKILL.md) | Monitor what people actually say about a brand, product, competitor, or topic on Reddit — mentions, sentiment, the communities driving the conversation, and verbatim voice-of-customer quotes — then optionally layer in YouTube channel/video engagement. Routes keyword and community monitoring to a Reddit scraper with built-in sentiment scoring, aggregates sentiment and themes, and surfaces the strongest quotes. Use when a user asks to track brand mentions, run social listening, do voice-of-customer research, gauge sentiment about a product or competitor, find Reddit discussions about a topic, monitor a subreddit, or analyze a YouTube channel's engagement. | [Renzo Madueno](https://github.com/renzomacar) |
| [`apify-tech-stack-prospecting`](skills/apify-tech-stack-prospecting/SKILL.md) | Discover and qualify B2B prospects by their tech stack. Chains Google Search signal queries to find companies using specific technologies, contact-info scraping to extract decision-maker emails and phones, and LinkedIn company enrichment to add firmographic data (size, industry, headcount). Use when user asks to find companies using a specific framework or tool, build a prospect list by technology, identify companies by language or framework, find companies integrating AI into their products, locate devtools customers, qualify engineering leads by stack, or wants a list of companies to reach out to based on what they're built on. | [Wilbur Suero](https://github.com/wilburhimself) |
| [`apify-verified-email-finder`](skills/apify-verified-email-finder/SKILL.md) | Builds a list of verified business emails from Google Maps, Google SERPs, or a user-supplied URL list. Verification happens inside the same Apify run — no third-party verifier needed. Use when user asks to find verified emails, build a leads list, scrape emails from Maps or SERP, verify emails for a URL list, or find an Apollo / Hunter alternative. | [Daniela Ryplová](https://github.com/danielarypl) |
| [`apify-x-twitter-data`](skills/apify-x-twitter-data/SKILL.md) | Collect public X/Twitter tweets, timelines, search results, followers, following, lists, and community member datasets with Xquik Apify Actors. Use when user asks for X/Twitter data extraction, social listening, audience analysis, creator research, follower exports, tweet exports, or list/community analysis. | [Burak](https://github.com/kriptoburak) |
| [`apify-x402-agentic-wallet`](skills/apify-x402-agentic-wallet/SKILL.md) | Discover, pay for, and run any Apify Actor by paying USDC on Base over the x402 protocol with a Coinbase Agentic Wallet (awal) — no Apify account or API key. You buy one small, spend-capped prepaid Apify token, then run as many Actors as the request needs with it. Use when the user wants to use Apify tools without signing up, pay per use with crypto / USDC, set up an agentic wallet, mentions "x402", "awal", "agentic wallet", "Coinbase wallet", "pay with USDC", "no API key", or asks to pull live web data (social media, search, maps, marketplaces, news) while paying on-chain per use. | [Martin Forejt](https://github.com/martinforejt) |
| [`apify-youtube-creator-research`](skills/apify-youtube-creator-research/SKILL.md) | Research YouTube channels, videos, Shorts, playlists, search results, comments, and creator positioning using Apify Actors. Use when the user asks for YouTube competitor analysis, creator research, content strategy, keyword/video discovery, audience comment mining, Shorts analysis, sponsor/brand mention discovery, or channel performance benchmarking. | — |
<!-- END_SKILLS_TABLE -->

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) — 1-minute setup. Eligible PRs qualify for the [community bounty](#bounty).

## For AI agents

See [agents/AGENTS.md](agents/AGENTS.md) — same content as this README plus the contributing guide, in a format optimised for autonomous agents.

## Prerequisites

- [Apify account](https://apify.com)
- (Optional) [Apify CLI](https://docs.apify.com/cli): `npm install -g apify-cli`
- Authentication: `apify login` or `APIFY_TOKEN` env var ([get a token](https://console.apify.com/settings/integrations))

## Support

- [Apify Documentation](https://docs.apify.com)
- [Apify Discord](https://discord.gg/jyEM2PRvMU)
- [Agent Skills Specification](https://agentskills.io/specification)
