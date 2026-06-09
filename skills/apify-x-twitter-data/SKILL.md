---
name: apify-x-twitter-data
description: Collect public X/Twitter tweets, timelines, search results, followers, following, lists, and community member datasets with Xquik Apify Actors. Use when user asks for X/Twitter data extraction, social listening, audience analysis, creator research, follower exports, tweet exports, or list/community analysis.
author: Burak
author_url: https://github.com/kriptoburak
---

# X/Twitter Data Collection

Collect public X/Twitter tweet and profile-relation datasets with Xquik Apify Actors, then summarize or export the results.

**CLI rules:** Always pass `--user-agent apify-awesome-skills/apify-x-twitter-data`, `--json` for Actor metadata and calls, and `--format json` or `--format csv` for dataset exports. Append `2>/dev/null` so CLI progress messages do not break JSON parsing.

## Prerequisites

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- `jq` for inspecting JSON samples
- Authentication through `apify login` or an `APIFY_TOKEN` environment variable

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Classify the user's X/Twitter data goal
- [ ] Step 2: Pick the right Xquik Actor
- [ ] Step 3: Fetch the Actor schema and build capped input
- [ ] Step 4: Run the Actor and fetch the dataset
- [ ] Step 5: Deliver a concise summary or saved export
```

### Step 1: Classify the Goal

| User asks for | Intent |
|---------------|--------|
| tweets, tweet URL, post URL, thread, status ID | `tweet-lookup` |
| search query, keyword, hashtag, language, date window | `tweet-search` |
| account timeline, posts by handle, tweets from user | `timeline` |
| followers, following, verified followers | `profile-relation` |
| list members, list subscribers | `list-relation` |
| community members | `community-relation` |

If the request mixes tweet content and follower data, run the tweet Actor first, then run the follower Actor only if the user still needs relationship data.

### Step 2: Pick an Actor

| Intent | Actor ID | Best for |
|--------|----------|----------|
| `tweet-lookup` | `xquik/x-tweet-scraper` | Tweet URLs, tweet IDs, and profile URLs |
| `tweet-search` | `xquik/x-tweet-scraper` | Search terms, hashtags, account queries, and date windows |
| `timeline` | `xquik/x-tweet-scraper` | Public posts from one or more handles |
| `profile-relation` | `xquik/x-follower-scraper` | Followers, following, and verified followers |
| `list-relation` | `xquik/x-follower-scraper` | List members and list subscribers |
| `community-relation` | `xquik/x-follower-scraper` | Community member exports |

### Step 3: Fetch Schema and Build Input

Fetch the current schema before composing input:

```bash
apify actors info "xquik/x-tweet-scraper" \
  --input --user-agent apify-awesome-skills/apify-x-twitter-data --json 2>/dev/null

apify actors info "xquik/x-follower-scraper" \
  --input --user-agent apify-awesome-skills/apify-x-twitter-data --json 2>/dev/null
```

Use conservative defaults unless the user asks for more:

| Intent | Default cap | Key fields |
|--------|-------------|------------|
| `tweet-lookup` | 25 tweets | `startUrls`, `tweetIds`, `maxItems` |
| `tweet-search` | 100 tweets per term | `searchTerms`, `queryType`, `maxItems`, `includeSearchTerms` |
| `timeline` | 100 tweets per handle | `twitterHandles`, `maxItems` |
| `profile-relation` | 200 profiles | `twitterHandles`, `relation`, `maxItems`, `outputMode` |
| `list-relation` | 200 profiles | `startUrls` or `listIds`, `relation`, `maxItems` |
| `community-relation` | 200 profiles | `startUrls` or `communityIds`, `relation`, `maxItems` |

Confirm before large runs because they use more Apify credits and can take longer.

### Step 4: Run the Actor

Tweet search example:

```bash
apify actors call "xquik/x-tweet-scraper" \
  -i '{"searchTerms":["from:apify since:2026-01-01"],"queryType":"Latest","maxItems":50,"includeSearchTerms":true}' \
  --user-agent apify-awesome-skills/apify-x-twitter-data --json 2>/dev/null
```

Tweet URL example:

```bash
apify actors call "xquik/x-tweet-scraper" \
  -i '{"startUrls":[{"url":"https://x.com/apify/status/1234567890"}],"maxItems":25}' \
  --user-agent apify-awesome-skills/apify-x-twitter-data --json 2>/dev/null
```

Follower export example:

```bash
apify actors call "xquik/x-follower-scraper" \
  -i '{"twitterHandles":["apify"],"relation":"followers","maxItems":200,"outputMode":"compact"}' \
  --user-agent apify-awesome-skills/apify-x-twitter-data --json 2>/dev/null
```

From the run JSON, capture `.id`, `.status`, `.defaultDatasetId`, and `.consoleUrl`. If `.status` is not `SUCCEEDED`, open `.consoleUrl` and inspect the run logs before retrying.

### Step 5: Fetch and Deliver Results

Fetch a small sample first:

```bash
apify datasets get-items DATASET_ID --limit 5 \
  --user-agent apify-awesome-skills/apify-x-twitter-data --format json 2>/dev/null
```

Save a JSON export:

```bash
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-x-twitter-data --format json 2>/dev/null > x-twitter-data.json
```

Save a CSV export:

```bash
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-x-twitter-data --format csv 2>/dev/null > x-twitter-data.csv
```

For tweet datasets, summarize count, query or target, time range, top authors, engagement fields present, and representative URLs. For profile-relation datasets, summarize count, relation type, target handles or URLs, verification split if present, follower-count range if present, and the export filename.

## Troubleshooting

- Auth error: run `apify login`, or set `APIFY_TOKEN`.
- `Actor not found`: verify the Actor ID from the routing table.
- Empty results: reduce filters, test one handle or URL, and switch `queryType` from `Top` to `Latest` for search.
- Large or slow run: lower `maxItems` or split targets into smaller batches.
