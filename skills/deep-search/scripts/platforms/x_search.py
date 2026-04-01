# deep-search X/Twitter platform module
# Backend 1: Bird CLI (vendored GraphQL search with 4-stage retry)
# Backend 2: Browser Advanced Search URL (via x-search skill)
# Backend 3: xAI Grok x_search (AI-mediated)
# Bird CLI derived from last30days v2.9.5 by Matt Van Horn (MIT License)

"""X/Twitter search with cascading backends."""

import json
import os
import re
import signal
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.schema import XResult, Engagement
from lib.query import extract_core_subject, extract_compound_terms
from lib.relevance import token_overlap_relevance
from lib.dates import get_date_range

# Bird CLI paths
_BIRD_SEARCH_MJS = Path(__file__).resolve().parent.parent.parent.parent / "last30days" / "scripts" / "lib" / "vendor" / "bird-search" / "bird-search.mjs"
_BIRD_AUTH_ENV_PATHS = [
    Path.home() / "workspace" / "memory" / "secrets" / "bird-x-auth.env",
    Path.home() / "workspace" / "credentials" / "bird-x-auth.env",
    Path.home() / ".config" / "last30days" / ".env",
]

DEPTH_CONFIG = {"quick": 12, "default": 30, "deep": 60}


def _log(msg: str):
    sys.stderr.write(f"[X] {msg}\n")
    sys.stderr.flush()


def _load_bird_credentials() -> Dict[str, str]:
    """Load AUTH_TOKEN and CT0 from first available env file."""
    creds = {}
    for env_path in _BIRD_AUTH_ENV_PATHS:
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                val = val.strip().strip("'\"")
                if key.strip() in ("AUTH_TOKEN", "CT0"):
                    creds[key.strip()] = val
        if creds.get("AUTH_TOKEN") and creds.get("CT0"):
            _log(f"Loaded Bird credentials from {env_path}")
            break
    return creds


def _bird_env() -> Dict[str, str]:
    """Build env dict for Bird subprocess."""
    env = os.environ.copy()
    creds = _load_bird_credentials()
    env.update(creds)
    if creds:
        env["BIRD_DISABLE_BROWSER_COOKIES"] = "1"
    return env


def _is_bird_available() -> bool:
    """Check if Bird CLI is usable."""
    return _BIRD_SEARCH_MJS.exists() and shutil.which("node") is not None


def _run_bird_search(query: str, count: int, timeout: int = 45) -> Dict[str, Any]:
    """Run vendored bird-search.mjs."""
    cmd = ["node", str(_BIRD_SEARCH_MJS), query, "--count", str(count), "--json"]
    preexec = os.setsid if hasattr(os, 'setsid') else None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, preexec_fn=preexec, env=_bird_env())
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                proc.kill()
            proc.wait(timeout=5)
            return {"error": f"Timed out after {timeout}s", "items": []}
        if proc.returncode != 0:
            return {"error": (stderr or "").strip()[:200], "items": []}
        output = (stdout or "").strip()
        if not output:
            return {"items": []}
        return json.loads(output)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}", "items": []}
    except Exception as e:
        return {"error": str(e), "items": []}


def _parse_bird_response(response: Dict[str, Any], query: str = "") -> List[Dict[str, Any]]:
    """Parse Bird JSON into normalized item dicts."""
    items = []
    raw = response if isinstance(response, list) else response.get("items", response.get("tweets", []))
    if not isinstance(raw, list):
        return items

    for i, tweet in enumerate(raw):
        if not isinstance(tweet, dict):
            continue
        url = tweet.get("permanent_url") or tweet.get("url", "")
        if not url and tweet.get("id"):
            author = tweet.get("author", {}) or tweet.get("user", {})
            sn = author.get("username") or author.get("screen_name", "")
            if sn:
                url = f"https://x.com/{sn}/status/{tweet['id']}"
        if not url:
            continue

        date = None
        created_at = tweet.get("createdAt") or tweet.get("created_at", "")
        if created_at:
            try:
                if len(created_at) > 10 and created_at[10] == "T":
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                date = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass

        author_info = tweet.get("author", {}) or tweet.get("user", {})
        handle = (author_info.get("username") or author_info.get("screen_name", "")).lstrip("@")
        name = author_info.get("name") or author_info.get("displayName", "")

        eng = {
            "likes": tweet.get("likeCount") or tweet.get("like_count") or tweet.get("favorite_count"),
            "reposts": tweet.get("retweetCount") or tweet.get("retweet_count"),
            "replies": tweet.get("replyCount") or tweet.get("reply_count"),
            "quotes": tweet.get("quoteCount") or tweet.get("quote_count"),
        }
        for k in eng:
            if eng[k] is not None:
                try:
                    eng[k] = int(eng[k])
                except (ValueError, TypeError):
                    eng[k] = None

        text = str(tweet.get("text", tweet.get("full_text", ""))).strip()[:500]
        items.append({
            "text": text,
            "url": url,
            "handle": handle,
            "name": name,
            "date": date,
            "engagement": eng,
            "relevance": token_overlap_relevance(query, text) if query else 0.7,
        })
    return items


def _search_bird(topic: str, from_date: str, depth: str = "default") -> List[Dict[str, Any]]:
    """Search X via Bird CLI with 4-stage retry."""
    if not _is_bird_available():
        _log("Bird CLI not available")
        return []

    creds = _load_bird_credentials()
    if not creds.get("AUTH_TOKEN"):
        _log("No Bird auth credentials")
        return []

    count = DEPTH_CONFIG.get(depth, 30)
    timeout = {"quick": 30, "default": 45, "deep": 60}.get(depth, 45)
    core = extract_core_subject(topic, max_words=5, strip_suffixes=True)

    # Stage 1: Full cleaned query
    query = f"{core} since:{from_date}"
    _log(f"Bird search stage 1: {query}")
    response = _run_bird_search(query, count, timeout)
    items = _parse_bird_response(response, query=core)
    if items:
        return items

    # Stage 2: OR-group compound terms
    core_words = core.split()
    if len(core_words) >= 2:
        compounds = extract_compound_terms(topic)
        if compounds:
            or_parts = ' OR '.join(f'"{t}"' for t in compounds[:3])
            query = f"({or_parts}) since:{from_date}"
            _log(f"Bird search stage 2 (OR groups): {query}")
            response = _run_bird_search(query, count, timeout)
            items = _parse_bird_response(response, query=core)
            if items:
                return items

    # Stage 3: Truncate to first 2 words
    if len(core_words) > 2:
        shorter = ' '.join(core_words[:2])
        query = f"{shorter} since:{from_date}"
        _log(f"Bird search stage 3 (truncated): {query}")
        response = _run_bird_search(query, count, timeout)
        items = _parse_bird_response(response, query=core)
        if items:
            return items

    # Stage 4: Strongest single token
    low_signal = {'trending', 'hottest', 'hot', 'popular', 'viral', 'best', 'top',
                  'latest', 'new', 'plugin', 'plugins', 'skill', 'skills', 'tool', 'tools'}
    candidates = [w for w in core_words if w.lower() not in low_signal]
    if candidates:
        strongest = max(candidates, key=len)
        query = f"{strongest} since:{from_date}"
        _log(f"Bird search stage 4 (strongest token): {query}")
        response = _run_bird_search(query, count, timeout)
        items = _parse_bird_response(response, query=core)

    return items


def _search_xai(topic: str, from_date: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Search via xAI Grok x_search tool."""
    xai_script = Path.home() / ".openclaw" / "skills" / "x-search" / "scripts" / "xai-search.py"
    if not xai_script.exists():
        return []

    # Check for API key
    key_path = Path.home() / "workspace" / "memory" / "secrets" / "xai-key.txt"
    alt_key = Path.home() / ".openclaw" / "secrets" / "xai-key.txt"
    has_key = key_path.exists() or alt_key.exists() or os.environ.get("XAI_API_KEY")
    if not has_key:
        return []

    _log("Falling back to xAI Grok search")
    try:
        result = subprocess.run(
            ["python3", str(xai_script), "--topic", topic, "--max-results", str(max_results),
             "--scored", "--format", "json"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            _log(f"xAI search failed: {result.stderr[:200]}")
            return []
        data = json.loads(result.stdout)
        if isinstance(data, list):
            return data
        return data.get("posts", data.get("results", []))
    except Exception as e:
        _log(f"xAI search error: {e}")
        return []


def search(topic: str, from_date: str, to_date: str, depth: str = "default") -> List[XResult]:
    """Search X/Twitter with cascading backends: Bird → xAI Grok.

    Note: Browser backend is not automated here (requires browser tool interaction).
    The orchestrator can fall back to browser if both backends fail.

    Args:
        topic: Search topic
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        depth: quick/default/deep

    Returns:
        List of XResult
    """
    core = extract_core_subject(topic, max_words=5, strip_suffixes=True)

    # Backend 1: Bird CLI
    raw_items = _search_bird(topic, from_date, depth)

    # Backend 2: xAI Grok (if Bird returned nothing)
    if not raw_items:
        max_results = DEPTH_CONFIG.get(depth, 30)
        raw_items = _search_xai(topic, from_date, max_results)

    if not raw_items:
        _log("All X backends returned 0 results")
        return []

    # Normalize to XResult
    results = []
    seen_urls = set()
    for i, item in enumerate(raw_items):
        url = item.get("url", "")
        if url in seen_urls:
            continue
        if url:
            seen_urls.add(url)

        eng_data = item.get("engagement") or {}
        results.append(XResult(
            id=f"X{i+1}",
            text=item.get("text", "")[:500],
            title=item.get("text", "")[:100],  # Use first 100 chars as title for scoring
            url=url,
            date=item.get("date"),
            date_confidence="high" if item.get("date") else "low",
            author_handle=item.get("handle", item.get("author_handle", "")),
            author_name=item.get("name", item.get("author_name", "")),
            engagement=Engagement(
                likes=eng_data.get("likes"),
                reposts=eng_data.get("reposts"),
                replies=eng_data.get("replies"),
                quotes=eng_data.get("quotes"),
            ),
            relevance=item.get("relevance", token_overlap_relevance(core, item.get("text", ""))),
            why_relevant=f"X @{item.get('handle', item.get('author_handle', '?'))}: {item.get('text', '')[:50]}",
        ))

    # Date filter
    filtered = [r for r in results if not r.date or (from_date <= r.date <= to_date)]
    if len(filtered) >= 3:
        results = filtered

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="X/Twitter deep-search")
    parser.add_argument("topic", help="Search topic")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--depth", default="default", choices=["quick", "default", "deep"])
    args = parser.parse_args()

    from_date, to_date = get_date_range(args.days)
    results = search(args.topic, from_date, to_date, args.depth)

    for r in results:
        likes = r.engagement.likes or 0
        print(f"[{r.date or '????'}] @{r.author_handle}: {r.text[:100]} (❤️{likes}) rel={r.relevance:.2f}")
    print(f"\n{len(results)} results")
