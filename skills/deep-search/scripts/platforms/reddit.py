# deep-search Reddit platform module
# Primary: reddit-research OAuth CLI
# Fallback: Reddit JSON API (/.json)

"""Reddit search via OAuth scraper CLI + JSON API fallback."""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.schema import RedditResult, Engagement
from lib.query import extract_core_subject
from lib.query_type import detect_query_type
from lib.relevance import token_overlap_relevance
from lib import http
from lib.dates import get_date_range, timestamp_to_date

REDDIT_RESEARCH_CLI = os.path.expanduser("~/.local/bin/reddit-research")
REDDIT_SCRAPER_DIR = os.path.expanduser("~/tools/reddit-universal-scraper")

# Subreddit discovery: keyword → likely subreddits
# Used when we don't know which subs to search
SUBREDDIT_MAP = {
    "ai": ["artificial", "MachineLearning", "LocalLLaMA", "OpenAI", "ClaudeAI", "singularity"],
    "coding": ["programming", "learnprogramming", "webdev", "coding", "ExperiencedDevs"],
    "python": ["Python", "learnpython", "django", "flask"],
    "javascript": ["javascript", "webdev", "reactjs", "node", "nextjs"],
    "startup": ["startups", "Entrepreneur", "SaaS", "smallbusiness", "indiehackers"],
    "marketing": ["marketing", "digitalmarketing", "SEO", "PPC", "socialmedia", "content_marketing"],
    "video": ["VideoEditing", "Filmmakers", "videography", "AfterEffects", "premiere"],
    "design": ["graphic_design", "web_design", "UI_Design", "userexperience"],
    "crypto": ["CryptoCurrency", "Bitcoin", "ethereum", "defi"],
    "finance": ["personalfinance", "investing", "stocks", "wallstreetbets"],
    "gaming": ["gaming", "pcgaming", "Games", "gamedev"],
    "music": ["WeAreTheMusicMakers", "musicproduction", "edmproduction"],
    "productivity": ["productivity", "selfimprovement", "getdisciplined"],
    "business": ["Entrepreneur", "smallbusiness", "business", "ecommerce"],
    "automation": ["automation", "nocode", "zapier", "n8n_io"],
    "agent": ["AI_Agents", "LangChain", "LocalLLaMA", "OpenAI"],
}

REDDIT_NOISE = frozenset({
    'best', 'top', 'good', 'great', 'awesome', 'killer',
    'latest', 'new', 'news', 'update', 'updates',
    'trending', 'hottest', 'popular',
    'practices', 'features', 'tips',
    'recommendations', 'advice',
    'prompt', 'prompts', 'prompting',
    'methods', 'strategies', 'approaches',
    'how', 'to', 'the', 'a', 'an', 'for', 'with',
    'of', 'in', 'on', 'is', 'are', 'what', 'which',
    'guide', 'tutorial', 'using',
})


def _log(msg: str):
    sys.stderr.write(f"[Reddit] {msg}\n")
    sys.stderr.flush()


def _discover_subreddits(topic: str, max_subs: int = 5) -> List[str]:
    """Discover likely subreddits from topic keywords."""
    core = extract_core_subject(topic, noise=REDDIT_NOISE).lower()
    words = core.split()

    candidates = set()
    for word in words:
        for key, subs in SUBREDDIT_MAP.items():
            if word in key or key in word:
                candidates.update(subs)

    # If no keyword matches, use broad defaults
    if not candidates:
        qtype = detect_query_type(topic)
        if qtype in ("product", "opinion"):
            candidates = {"technology", "software", "tools"}
        elif qtype == "how_to":
            candidates = {"learnprogramming", "webdev", "technology"}
        else:
            candidates = {"technology", "news", "Futurology"}

    return list(candidates)[:max_subs]


def _run_scraper(subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Run reddit-research CLI for a subreddit and parse results.

    Returns list of raw post dicts from SQLite DB.
    """
    if not os.path.exists(REDDIT_RESEARCH_CLI):
        return []

    cmd = [
        REDDIT_RESEARCH_CLI, subreddit,
        "--mode", "history",
        "--limit", str(limit),
        "--no-comments", "--no-media",
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if result.returncode != 0:
            _log(f"Scraper failed for r/{subreddit}: {result.stderr[:200]}")
            return []
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        _log(f"Scraper error for r/{subreddit}: {e}")
        return []

    # Read from SQLite DB
    db_path = os.path.join(REDDIT_SCRAPER_DIR, "data", "reddit_scraper.db")
    if not os.path.exists(db_path):
        return []

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """SELECT id, title, selftext, url, permalink, score, num_comments,
                      upvote_ratio, created_utc, subreddit
               FROM posts
               WHERE subreddit = ?
               ORDER BY created_utc DESC
               LIMIT ?""",
            (subreddit, limit),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        _log(f"DB read failed: {e}")
        return []


def _search_json_api(subreddit: str, query: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Search a subreddit via Reddit JSON API (no auth, 429-prone)."""
    from urllib.parse import urlencode, quote_plus
    url = f"https://www.reddit.com/r/{subreddit}/search.json?{urlencode({'q': query, 'restrict_sr': 'on', 'sort': 'relevance', 't': 'month', 'limit': str(limit)})}"

    try:
        data = http.request("GET", url, timeout=15, retries=2)
        children = data.get("data", {}).get("children", [])
        return [c.get("data", {}) for c in children if c.get("kind") == "t3"]
    except http.HTTPError as e:
        if e.status_code == 429:
            _log(f"Reddit 429 rate limited for r/{subreddit}")
        else:
            _log(f"JSON API failed for r/{subreddit}: {e}")
        return []
    except Exception as e:
        _log(f"JSON API failed for r/{subreddit}: {e}")
        return []


def _normalize_post(post: Dict[str, Any], idx: int, source_label: str, query: str) -> RedditResult:
    """Normalize a raw Reddit post dict into RedditResult."""
    permalink = post.get("permalink", "")
    url = f"https://www.reddit.com{permalink}" if permalink and "reddit.com" not in permalink else post.get("url", "")

    title = str(post.get("title", "")).strip()
    selftext = str(post.get("selftext", ""))[:500]

    # Relevance: title-first scoring
    title_score = token_overlap_relevance(query, title)
    if selftext.strip():
        body_score = token_overlap_relevance(query, selftext)
        relevance = round(0.75 * title_score + 0.25 * max(title_score, body_score), 2)
    else:
        relevance = title_score

    created_utc = post.get("created_utc")
    date_str = timestamp_to_date(float(created_utc)) if created_utc else None

    return RedditResult(
        id=f"R{idx}",
        title=title,
        url=url,
        date=date_str,
        date_confidence="high" if date_str else "low",
        subreddit=str(post.get("subreddit", "")).strip(),
        selftext=selftext,
        engagement=Engagement(
            score=post.get("score") or post.get("ups", 0),
            num_comments=post.get("num_comments", 0),
            upvote_ratio=post.get("upvote_ratio"),
        ),
        relevance=relevance,
        why_relevant=f"Reddit r/{post.get('subreddit', '?')}: {title[:50]}",
    )


def _enrich_with_comments(results: List[RedditResult], max_enrich: int = 5) -> List[RedditResult]:
    """Enrich top results with comment data via JSON API."""
    for r in results[:max_enrich]:
        permalink = ""
        if r.url and "reddit.com" in r.url:
            from urllib.parse import urlparse
            path = urlparse(r.url).path
            if path:
                permalink = path

        if not permalink:
            continue

        try:
            data = http.get_reddit_json(permalink, timeout=10, retries=1)
            if not isinstance(data, list) or len(data) < 2:
                continue

            comments_listing = data[1]
            children = comments_listing.get("data", {}).get("children", [])

            top_comments = []
            insights = []
            for c in children[:10]:
                if c.get("kind") != "t1":
                    continue
                cd = c.get("data", {})
                body = cd.get("body", "")
                if not body or body in ("[deleted]", "[removed]"):
                    continue
                author = cd.get("author", "[deleted]")
                if author in ("[deleted]", "[removed]", "AutoModerator"):
                    continue

                top_comments.append({
                    "score": cd.get("score", 0),
                    "author": author,
                    "excerpt": body[:300],
                })

                if len(body) >= 30:
                    insight = body[:150]
                    for j, ch in enumerate(insight):
                        if ch in '.!?' and j > 50:
                            insight = insight[:j+1]
                            break
                    else:
                        if len(body) > 150:
                            insight = insight.rstrip() + "..."
                    insights.append(insight)

            top_comments.sort(key=lambda x: x.get("score", 0), reverse=True)
            r.top_comments = top_comments[:5]
            r.comment_insights = insights[:5]

        except Exception as e:
            _log(f"Comment enrichment failed: {e}")
            continue

    return results


def search(topic: str, from_date: str, to_date: str, depth: str = "default") -> List[RedditResult]:
    """Search Reddit. OAuth scraper primary, JSON API fallback.

    Args:
        topic: Search topic
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        depth: quick/default/deep

    Returns:
        List of RedditResult
    """
    core = extract_core_subject(topic, noise=REDDIT_NOISE)
    subs = _discover_subreddits(topic, max_subs=5 if depth != "quick" else 3)
    _log(f"Searching Reddit for '{core}' in subreddits: {subs}")

    all_posts = []
    has_scraper = os.path.exists(REDDIT_RESEARCH_CLI)

    for sub in subs:
        limit = {"quick": 15, "default": 25, "deep": 50}.get(depth, 25)

        if has_scraper:
            # Primary: OAuth scraper
            posts = _run_scraper(sub, limit)
            if posts:
                _log(f"  OAuth scraper: {len(posts)} posts from r/{sub}")
                all_posts.extend(posts)
                continue

        # Fallback: JSON API
        posts = _search_json_api(sub, core, limit)
        if posts:
            _log(f"  JSON API: {len(posts)} posts from r/{sub}")
            all_posts.extend(posts)

    # Normalize
    results = []
    seen_ids = set()
    for i, post in enumerate(all_posts):
        pid = post.get("id", "")
        if pid and pid in seen_ids:
            continue
        if pid:
            seen_ids.add(pid)
        r = _normalize_post(post, i + 1, "search", core)

        # Date filter
        if r.date and (r.date < from_date or r.date > to_date):
            continue
        results.append(r)

    _log(f"After dedup + date filter: {len(results)} posts")

    # Sort by engagement
    results.sort(key=lambda r: (r.engagement.score or 0), reverse=True)

    # Re-index
    for i, r in enumerate(results):
        r.id = f"R{i+1}"

    # Enrich top results with comments
    enrich_limit = {"quick": 3, "default": 5, "deep": 8}.get(depth, 5)
    results = _enrich_with_comments(results, enrich_limit)

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reddit deep-search")
    parser.add_argument("topic", help="Search topic")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--depth", default="default", choices=["quick", "default", "deep"])
    args = parser.parse_args()

    from_date, to_date = get_date_range(args.days)
    results = search(args.topic, from_date, to_date, args.depth)

    for r in results:
        comments = f"💬{len(r.top_comments)}" if r.top_comments else ""
        print(f"[{r.date or '????'}] r/{r.subreddit}: {r.title[:80]} (⬆{r.engagement.score} 💬{r.engagement.num_comments}) rel={r.relevance:.2f} {comments}")
    print(f"\n{len(results)} results")
