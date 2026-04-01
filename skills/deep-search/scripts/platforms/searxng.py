# deep-search SearXNG platform module
# Local metasearch via localhost:8888

"""Web search via self-hosted SearXNG. Free, no API key."""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import http
from lib.schema import SearXNGResult, Engagement
from lib.relevance import token_overlap_relevance
from lib.query import extract_core_subject
from lib.dates import get_date_range

SEARXNG_URL = "http://localhost:8888/search"


def _log(msg: str):
    sys.stderr.write(f"[SearXNG] {msg}\n")
    sys.stderr.flush()


# Date extraction patterns (the "Date Detective" from last30days websearch.py)
_URL_DATE_PATTERN = re.compile(r'/(\d{4})/(\d{2})/(\d{2})/')
_SNIPPET_DATE_PATTERNS = [
    re.compile(r'(\w+ \d{1,2},? \d{4})'),        # "January 24, 2026" or "Jan 24 2026"
    re.compile(r'(\d{1,2} \w+ \d{4})'),            # "24 January 2026"
    re.compile(r'(\d{4}-\d{2}-\d{2})'),             # "2026-01-24"
]
_RELATIVE_DATE_PATTERNS = [
    (re.compile(r'(\d+)\s*(?:day|days)\s*ago', re.I), lambda m: int(m.group(1))),
    (re.compile(r'(\d+)\s*(?:hour|hours|hr|hrs)\s*ago', re.I), lambda m: 0),
    (re.compile(r'(\d+)\s*(?:week|weeks)\s*ago', re.I), lambda m: int(m.group(1)) * 7),
    (re.compile(r'(\d+)\s*(?:month|months)\s*ago', re.I), lambda m: int(m.group(1)) * 30),
    (re.compile(r'yesterday', re.I), lambda m: 1),
    (re.compile(r'today', re.I), lambda m: 0),
]

_MONTH_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
    'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
    'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12,
}


def _extract_date_from_url(url: str) -> Optional[str]:
    """Extract YYYY-MM-DD from URL path patterns like /2026/01/24/."""
    m = _URL_DATE_PATTERN.search(url)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 2020 <= y <= 2030 and 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"
    return None


def _parse_written_date(text: str) -> Optional[str]:
    """Parse 'January 24, 2026' or '24 January 2026' to YYYY-MM-DD."""
    # "Month Day, Year"
    m = re.match(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', text)
    if m:
        month_name = m.group(1).lower()
        if month_name in _MONTH_MAP:
            mo = _MONTH_MAP[month_name]
            return f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(2)):02d}"
    # "Day Month Year"
    m = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', text)
    if m:
        month_name = m.group(2).lower()
        if month_name in _MONTH_MAP:
            mo = _MONTH_MAP[month_name]
            return f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(1)):02d}"
    return None


def _extract_date_from_snippet(snippet: str) -> Optional[str]:
    """Extract date from result snippet text."""
    for pattern in _SNIPPET_DATE_PATTERNS:
        m = pattern.search(snippet)
        if m:
            raw = m.group(1)
            # ISO date
            if re.match(r'\d{4}-\d{2}-\d{2}', raw):
                return raw
            # Written date
            parsed = _parse_written_date(raw)
            if parsed:
                return parsed

    # Relative dates
    from datetime import datetime, timedelta, timezone
    today = datetime.now(timezone.utc).date()
    for pattern, days_fn in _RELATIVE_DATE_PATTERNS:
        m = pattern.search(snippet)
        if m:
            days_ago = days_fn(m)
            d = today - timedelta(days=days_ago)
            return d.isoformat()

    return None


def _detect_date(url: str, snippet: str, title: str) -> tuple:
    """Detect date with confidence level. Returns (date_str, confidence)."""
    # URL dates are most reliable
    url_date = _extract_date_from_url(url)
    if url_date:
        return url_date, "high"

    # Snippet dates
    snippet_date = _extract_date_from_snippet(snippet)
    if snippet_date:
        return snippet_date, "med"

    # Title dates
    title_date = _extract_date_from_snippet(title)
    if title_date:
        return title_date, "med"

    return None, "low"


def search(topic: str, from_date: str, to_date: str, depth: str = "default",
           categories: str = "general", time_range: str = None) -> List[SearXNGResult]:
    """Search SearXNG and return normalized results.

    Args:
        topic: Search topic
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        depth: quick/default/deep
        categories: SearXNG categories (general, news, it, science, etc.)
        time_range: SearXNG time range filter (day, week, month, year)

    Returns:
        List of SearXNGResult
    """
    core = extract_core_subject(topic)
    limit = {"quick": 10, "default": 20, "deep": 30}.get(depth, 20)

    params = {
        "q": core,
        "format": "json",
        "categories": categories,
        "language": "en",
    }
    if time_range:
        params["time_range"] = time_range

    url = f"{SEARXNG_URL}?{urlencode(params)}"
    _log(f"Searching SearXNG for '{core}' (categories={categories})")

    try:
        response = http.request("GET", url, timeout=15, retries=2)
    except Exception as e:
        _log(f"SearXNG request failed: {e}")
        return []

    raw_results = response.get("results", [])
    _log(f"Got {len(raw_results)} results")

    results = []
    seen_urls = set()
    for i, r in enumerate(raw_results[:limit]):
        result_url = r.get("url", "")
        if result_url in seen_urls:
            continue
        if result_url:
            seen_urls.add(result_url)

        title = r.get("title", "")
        snippet = r.get("content", "")
        engine = r.get("engine", "")

        # Date detection
        date_str, confidence = _detect_date(result_url, snippet, title)

        # Relevance scoring
        rel = token_overlap_relevance(core, f"{title} {snippet}")

        results.append(SearXNGResult(
            id=f"W{i+1}",
            title=title,
            text=snippet,
            url=result_url,
            date=date_str,
            date_confidence=confidence,
            engine=engine,
            snippet=snippet[:300],
            engagement=Engagement(),  # No engagement data for web results
            relevance=rel,
            why_relevant=f"Web ({engine}): {title[:60]}",
        ))

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SearXNG deep-search")
    parser.add_argument("topic", help="Search topic")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--depth", default="default", choices=["quick", "default", "deep"])
    parser.add_argument("--categories", default="general")
    args = parser.parse_args()

    from_date, to_date = get_date_range(args.days)
    results = search(args.topic, from_date, to_date, args.depth, args.categories)

    for r in results:
        conf = {"high": "📅", "med": "📆", "low": "❓"}.get(r.date_confidence, "❓")
        print(f"{conf}[{r.date or '????'}] {r.title[:80]} ({r.engine}) rel={r.relevance:.2f}")
    print(f"\n{len(results)} results")
