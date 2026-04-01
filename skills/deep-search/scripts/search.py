#!/usr/bin/env python3
# deep-search orchestrator
# Parallel multi-platform search with unified scoring and cross-source convergence

"""Deep search: topic in → ranked multi-source results out."""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.dates import get_date_range
from lib.query import extract_core_subject
from lib.query_type import detect_query_type, is_source_enabled
from lib.score import score_items, sort_all, relevance_filter
from lib.dedupe import dedupe_items, cross_source_link
from lib.schema import SearchResult

# Platform search functions (lazy-loaded)
PLATFORMS = {
    "youtube": "platforms.youtube",
    "hackernews": "platforms.hackernews",
    "reddit": "platforms.reddit",
    "x": "platforms.x_search",
    "searxng": "platforms.searxng",
}


def _log(msg: str):
    sys.stderr.write(f"[deep-search] {msg}\n")
    sys.stderr.flush()


def _import_platform(name: str):
    """Lazy-import a platform module."""
    import importlib
    return importlib.import_module(PLATFORMS[name])


def _search_platform(name: str, topic: str, from_date: str, to_date: str, depth: str) -> List[SearchResult]:
    """Run search on a single platform. Returns list of SearchResult."""
    try:
        mod = _import_platform(name)
        return mod.search(topic, from_date, to_date, depth)
    except Exception as e:
        _log(f"{name} search failed: {e}")
        return []


def search(
    topic: str,
    days: int = 30,
    from_date: str = None,
    to_date: str = None,
    depth: str = "default",
    platforms: List[str] = None,
    max_results: int = 50,
) -> Dict[str, Any]:
    """Run multi-platform search.

    Args:
        topic: Search topic
        days: Days to look back (default 30, ignored if from_date/to_date set)
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        depth: quick/default/deep
        platforms: Explicit platform list (None = auto-select by query type)
        max_results: Max results to return

    Returns:
        Dict with 'results', 'query_type', 'platforms_searched', 'stats'
    """
    start = time.time()

    # Date range
    if not from_date or not to_date:
        from_date, to_date = get_date_range(days)

    # Query analysis
    core = extract_core_subject(topic)
    query_type = detect_query_type(topic)
    _log(f"Topic: '{topic}' → core: '{core}' → type: {query_type}")

    # Select platforms
    if platforms:
        selected = [p for p in platforms if p in PLATFORMS]
    else:
        selected = [p for p in PLATFORMS if is_source_enabled(p, query_type)]
    _log(f"Platforms: {selected}")

    # Parallel search
    all_results: Dict[str, List[SearchResult]] = {}
    with ThreadPoolExecutor(max_workers=len(selected)) as executor:
        futures = {
            executor.submit(_search_platform, name, topic, from_date, to_date, depth): name
            for name in selected
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results = future.result(timeout=180)
                all_results[name] = results
                _log(f"  {name}: {len(results)} results")
            except Exception as e:
                _log(f"  {name}: FAILED ({e})")
                all_results[name] = []

    # Per-source scoring, filtering, deduplication
    scored_by_source: Dict[str, List[SearchResult]] = {}
    for name, items in all_results.items():
        if not items:
            continue
        # Score
        items = score_items(items, query_type, max_days=days)
        # Filter low relevance
        items = relevance_filter(items, name)
        # Dedupe within source
        items.sort(key=lambda x: x.score, reverse=True)
        items = dedupe_items(items)
        scored_by_source[name] = items

    # Cross-source convergence linking
    source_lists = list(scored_by_source.values())
    if len(source_lists) > 1:
        cross_source_link(*source_lists)

    # Merge all sources
    merged = []
    for items in scored_by_source.values():
        merged.extend(items)

    # Sort by composite score
    merged = sort_all(merged, query_type)

    # Cap results
    merged = merged[:max_results]

    elapsed = time.time() - start

    # Stats
    stats = {
        "elapsed_seconds": round(elapsed, 1),
        "query_type": query_type,
        "core_query": core,
        "platforms_searched": list(scored_by_source.keys()),
        "platforms_failed": [p for p in selected if p not in scored_by_source or not scored_by_source[p]],
        "results_per_source": {k: len(v) for k, v in scored_by_source.items()},
        "total_results": len(merged),
        "cross_refs": sum(1 for r in merged if r.cross_refs),
    }

    return {"results": merged, "stats": stats}


def format_markdown(data: Dict[str, Any]) -> str:
    """Format search results as markdown."""
    stats = data["stats"]
    results = data["results"]

    lines = [
        f"# Deep Search: {stats['core_query']}",
        f"**Query type:** {stats['query_type']} | **Sources:** {', '.join(stats['platforms_searched'])} | **Results:** {stats['total_results']} | **Time:** {stats['elapsed_seconds']}s",
        "",
    ]

    if stats["platforms_failed"]:
        lines.append(f"⚠️ Failed: {', '.join(stats['platforms_failed'])}")
        lines.append("")

    for i, r in enumerate(results, 1):
        # Score badge
        if r.score >= 70:
            badge = "🟢"
        elif r.score >= 40:
            badge = "🟡"
        else:
            badge = "🔴"

        # Source badge
        source_emoji = {"youtube": "📺", "hackernews": "🟠", "reddit": "🔵", "x": "𝕏", "searxng": "🌐"}.get(r.source, "📄")

        # Cross-ref indicator
        xref = f" 🔗{len(r.cross_refs)}" if r.cross_refs else ""

        lines.append(f"{i}. {badge} {source_emoji} **{r.title or r.text[:80]}** (score: {r.score:.0f}{xref})")
        lines.append(f"   {r.url}")

        if r.date:
            lines.append(f"   📅 {r.date} | rel={r.relevance:.2f}")

        # Platform-specific extras
        if r.source == "youtube" and hasattr(r, 'highlights') and r.highlights:
            for h in r.highlights[:2]:
                lines.append(f"   💡 {h[:120]}")
        elif r.source == "reddit" and hasattr(r, 'comment_insights') and r.comment_insights:
            for ci in r.comment_insights[:2]:
                lines.append(f"   💬 {ci[:120]}")
        elif r.source == "hackernews" and hasattr(r, 'top_comments') and r.top_comments:
            for tc in r.top_comments[:2]:
                lines.append(f"   💬 {tc.get('text', '')[:120]}")

        lines.append("")

    if stats["cross_refs"]:
        lines.append(f"---\n🔗 **{stats['cross_refs']} cross-source convergences detected** (same topic discussed across multiple platforms)")

    return "\n".join(lines)


def format_json(data: Dict[str, Any]) -> str:
    """Format results as JSON."""
    serializable = {
        "stats": data["stats"],
        "results": [],
    }
    for r in data["results"]:
        item = {
            "id": r.id,
            "source": r.source,
            "title": r.title,
            "text": r.text[:200] if r.text else "",
            "url": r.url,
            "date": r.date,
            "score": round(r.score, 1),
            "relevance": round(r.relevance, 2),
            "cross_refs": r.cross_refs,
        }
        if r.engagement:
            eng = {}
            for field in ("likes", "reposts", "replies", "quotes", "views", "score", "num_comments"):
                v = getattr(r.engagement, field, None)
                if v is not None:
                    eng[field] = v
            if eng:
                item["engagement"] = eng
        serializable["results"].append(item)
    return json.dumps(serializable, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Deep search: multi-platform topic research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 search.py "AI video editing tools"
  python3 search.py "Claude Code" --days 7 --depth quick
  python3 search.py "startup funding 2026" --platforms reddit hackernews searxng
  python3 search.py "machine learning" --format json --max-results 20
        """,
    )
    parser.add_argument("topic", help="Search topic")
    parser.add_argument("--days", type=int, default=30, help="Days to look back (default: 30)")
    parser.add_argument("--from-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--depth", default="default", choices=["quick", "default", "deep"])
    parser.add_argument("--platforms", nargs="+", choices=list(PLATFORMS.keys()),
                        help="Explicit platforms (default: auto-select by query type)")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    parser.add_argument("--max-results", type=int, default=50)
    args = parser.parse_args()

    data = search(
        topic=args.topic,
        days=args.days,
        from_date=args.from_date,
        to_date=args.to_date,
        depth=args.depth,
        platforms=args.platforms,
        max_results=args.max_results,
    )

    if args.format == "json":
        print(format_json(data))
    else:
        print(format_markdown(data))


if __name__ == "__main__":
    main()
