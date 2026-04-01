---
name: deep-search
description: Multi-platform topic research across YouTube, HackerNews, Reddit, X/Twitter, and SearXNG. Unified scoring, deduplication, cross-source convergence detection. Use for deep research, content discovery, competitive intelligence, trend analysis. Each platform also usable standalone. Triggers on "deep search", "research this topic", "what are people saying about", "search everywhere for", "multi-source search", "find posts about".
---

# Deep Search

Multi-platform topic research with unified scoring. 5 platforms, parallel search, cross-source convergence detection.

## Triggers

- "deep search for X" or "research X across platforms"
- "what are people saying about X"
- "search everywhere for X"
- "find posts/content about X"
- Any multi-source research request

## Quick Start

```bash
# Full orchestrated search (auto-selects platforms by query type)
python3 ~/.openclaw/skills/deep-search/scripts/search.py "AI video editing tools"

# Quick search (fewer results, faster)
python3 ~/.openclaw/skills/deep-search/scripts/search.py "Claude Code" --days 7 --depth quick

# Specific platforms only
python3 ~/.openclaw/skills/deep-search/scripts/search.py "startup funding" --platforms reddit hackernews searxng

# JSON output
python3 ~/.openclaw/skills/deep-search/scripts/search.py "machine learning" --format json
```

## Platforms

| Platform | Auth | Backend |
|----------|------|---------|
| YouTube | None (yt-dlp) | Search + transcript extraction, no API key |
| HackerNews | None | Algolia API, free, unlimited |
| Reddit | OAuth token | OAuth scraper CLI primary, JSON API fallback |
| X/Twitter | Session cookies | Bird CLI (4-stage retry) → xAI Grok fallback |
| SearXNG | None | Local metasearch at localhost:8888 |

## Standalone Platform Use

Each platform module is independently callable:

```bash
# YouTube only
python3 ~/.openclaw/skills/deep-search/scripts/platforms/youtube.py "AI agents" --days 30

# HackerNews only
python3 ~/.openclaw/skills/deep-search/scripts/platforms/hackernews.py "Claude Code" --days 7

# Reddit only
python3 ~/.openclaw/skills/deep-search/scripts/platforms/reddit.py "best CRM tools" --days 30

# X/Twitter only
python3 ~/.openclaw/skills/deep-search/scripts/platforms/x_search.py "AI coding" --days 7

# SearXNG only
python3 ~/.openclaw/skills/deep-search/scripts/platforms/searxng.py "Claude Code tutorials"
```

## Importable Library

Other skills can import individual modules:

```python
from deep_search.platforms.youtube import search as yt_search
from deep_search.lib.query import extract_core_subject
from deep_search.lib.relevance import token_overlap_relevance
from deep_search.lib.score import score_items
```

## Query Type Intelligence

The orchestrator auto-classifies queries and selects platforms accordingly:

- **product** (price, buy, alternative): Reddit → X → YouTube → SearXNG
- **concept** (what is, explain): Reddit → HN → SearXNG → YouTube
- **opinion** (worth it, review): Reddit → X → YouTube → HN
- **how_to** (tutorial, setup): YouTube → Reddit → HN → SearXNG
- **comparison** (vs, compared to): Reddit → HN → YouTube → X
- **breaking_news** (latest, launched): X → Reddit → SearXNG → HN

## Scoring

Three-axis composite (0-100):
- **Relevance** (45%): token overlap scoring with synonym expansion
- **Recency** (25%): linear decay over configurable window
- **Engagement** (30%): platform-specific log-scaled formulas

SearXNG uses 55% relevance + 45% recency (no engagement data), with date-confidence adjustments and query-type-specific source penalties.

## Cross-Source Convergence

When the same topic appears across multiple platforms (e.g., a Reddit post and an X thread about the same tool), results are linked via `cross_refs`. This is a signal multiplier -- topics with cross-source convergence are more significant.

## Credential Locations

Configure credentials via environment variables or env files in your workspace:

- **X/Twitter:** Set `AUTH_TOKEN` and `CT0` in a `bird-x-auth.env` file, or install [Bird CLI](https://github.com/nicholasgasior/bird)
- **xAI Grok (fallback):** Set `XAI_API_KEY` environment variable or place key in `~/.openclaw/secrets/xai-key.txt`
- **Reddit:** Install and configure the `reddit-research` CLI with OAuth credentials
- **SearXNG:** Run a SearXNG instance (Docker recommended) on localhost:8888
- **YouTube:** Install [yt-dlp](https://github.com/yt-dlp/yt-dlp) — no API key needed
- **HackerNews:** No credentials needed (Algolia public API)

## CLI Arguments

```
search.py <topic> [options]

Options:
  --days N           Days to look back (default: 30)
  --from-date DATE   Start date (YYYY-MM-DD)
  --to-date DATE     End date (YYYY-MM-DD)
  --depth LEVEL      quick / default / deep
  --platforms P [P]  Explicit platforms (youtube hackernews reddit x searxng)
  --format FMT       markdown / json
  --max-results N    Max results (default: 50)
```

## Dependencies

Zero new dependencies. Uses only tools already on the system:
- Python 3.8+ (stdlib only -- no pip packages required)
- yt-dlp (YouTube search + transcripts)
- Node.js 22+ (Bird CLI for X search)
- SearXNG Docker container (localhost:8888)
- reddit-research CLI (OAuth scraper)
