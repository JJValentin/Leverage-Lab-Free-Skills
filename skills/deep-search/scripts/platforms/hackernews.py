# Derived from last30days v2.9.5 by Matt Van Horn (MIT License)
# https://github.com/mattvanhorn/last30days
# Adapted for deep-search schema

"""Hacker News search via Algolia API. Free, no auth required."""

import html
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import http
from lib.schema import HackerNewsResult, Engagement
from lib.query import extract_core_subject
from lib.relevance import token_overlap_relevance
from lib.dates import get_date_range

ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
ALGOLIA_ITEM_URL = "https://hn.algolia.com/api/v1/items"

DEPTH_CONFIG = {"quick": 15, "default": 30, "deep": 60}
ENRICH_LIMITS = {"quick": 3, "default": 5, "deep": 10}


def _log(msg: str):
    sys.stderr.write(f"[HN] {msg}\n")
    sys.stderr.flush()


def _date_to_unix(date_str: str) -> int:
    parts = date_str.split("-")
    dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]), tzinfo=timezone.utc)
    return int(dt.timestamp())


def _unix_to_date(ts: int) -> str:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def _strip_html(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r'<p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def _fetch_item_comments(object_id: str, max_comments: int = 5) -> Dict[str, Any]:
    """Fetch top-level comments for a story."""
    url = f"{ALGOLIA_ITEM_URL}/{object_id}"
    try:
        data = http.request("GET", url, timeout=15)
    except Exception as e:
        _log(f"Failed to fetch comments for {object_id}: {e}")
        return {"comments": [], "insights": []}

    children = data.get("children", [])
    real_comments = [c for c in children if c.get("text") and c.get("author")]
    real_comments.sort(key=lambda c: c.get("points") or 0, reverse=True)

    comments = []
    insights = []
    for c in real_comments[:max_comments]:
        text = _strip_html(c.get("text", ""))
        excerpt = text[:300] + "..." if len(text) > 300 else text
        comments.append({
            "author": c.get("author", ""),
            "text": excerpt,
            "points": c.get("points") or 0,
        })
        first_sentence = text.split(". ")[0].split("\n")[0][:200]
        if first_sentence:
            insights.append(first_sentence)

    return {"comments": comments, "insights": insights}


def search(topic: str, from_date: str, to_date: str, depth: str = "default") -> List[HackerNewsResult]:
    """Search HackerNews and return HackerNewsResult objects.

    Args:
        topic: Search topic
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        depth: quick/default/deep

    Returns:
        List of HackerNewsResult
    """
    count = DEPTH_CONFIG.get(depth, 30)
    from_ts = _date_to_unix(from_date)
    to_ts = _date_to_unix(to_date) + 86400

    core = extract_core_subject(topic)
    _log(f"Searching for '{core}' (raw: '{topic}', since {from_date}, count={count})")

    params = {
        "query": core,
        "tags": "story",
        "numericFilters": f"created_at_i>{from_ts},created_at_i<{to_ts},points>2",
        "hitsPerPage": str(count),
    }
    url = f"{ALGOLIA_SEARCH_URL}?{urlencode(params)}"

    try:
        response = http.request("GET", url, timeout=30)
    except Exception as e:
        _log(f"Search failed: {e}")
        return []

    hits = response.get("hits", [])
    _log(f"Found {len(hits)} stories")

    # Parse into results
    results = []
    for i, hit in enumerate(hits):
        object_id = hit.get("objectID", "")
        points = hit.get("points") or 0
        num_comments = hit.get("num_comments") or 0
        created_at_i = hit.get("created_at_i")
        date_str = _unix_to_date(created_at_i) if created_at_i else None

        article_url = hit.get("url") or ""
        hn_url = f"https://news.ycombinator.com/item?id={object_id}"

        # Blended relevance: Algolia rank + token overlap + engagement boost
        rank_score = max(0.3, 1.0 - (i * 0.02))
        engagement_boost = min(0.2, math.log1p(points) / 40)
        content_score = token_overlap_relevance(core, hit.get("title", ""))
        relevance = min(1.0, 0.6 * rank_score + 0.4 * content_score + engagement_boost)

        results.append(HackerNewsResult(
            id=f"HN{i+1}",
            title=hit.get("title", ""),
            url=hn_url,
            story_url=article_url,
            date=date_str,
            date_confidence="high" if date_str else "low",
            engagement=Engagement(score=points, num_comments=num_comments),
            relevance=round(relevance, 2),
            why_relevant=f"HN: {hit.get('title', '')[:60]}",
            extra={"object_id": object_id, "author": hit.get("author", "")},
        ))

    # Enrich top stories with comments
    enrich_limit = ENRICH_LIMITS.get(depth, 5)
    if results:
        by_points = sorted(range(len(results)), key=lambda i: results[i].engagement.score or 0, reverse=True)
        to_enrich = by_points[:enrich_limit]

        _log(f"Enriching top {len(to_enrich)} stories with comments")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(_fetch_item_comments, results[idx].extra["object_id"]): idx
                for idx in to_enrich
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result(timeout=15)
                    results[idx].top_comments = result["comments"]
                    results[idx].extra["comment_insights"] = result["insights"]
                except Exception:
                    pass

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HackerNews deep-search")
    parser.add_argument("topic", help="Search topic")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--depth", default="default", choices=["quick", "default", "deep"])
    args = parser.parse_args()

    from_date, to_date = get_date_range(args.days)
    results = search(args.topic, from_date, to_date, args.depth)

    for r in results:
        comments = f"💬{len(r.top_comments)}" if r.top_comments else ""
        print(f"[{r.date or '????'}] {r.title} (⬆{r.engagement.score} 💬{r.engagement.num_comments}) rel={r.relevance:.2f} {comments}")
    print(f"\n{len(results)} results")
