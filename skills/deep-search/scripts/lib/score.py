# Derived from last30days v2.9.5 by Matt Van Horn (MIT License)
# https://github.com/mattvanhorn/last30days
# Adapted for deep-search simplified schema (5 platforms)

"""Composite scoring engine for deep-search results."""

import math
import sys
from typing import List, Optional

from . import dates
from .schema import SearchResult, Engagement
from .query_type import QueryType, WEBSEARCH_PENALTY_BY_TYPE, TIEBREAKER_BY_TYPE

# Score weights for social platforms (has engagement data)
WEIGHT_RELEVANCE = 0.45
WEIGHT_RECENCY = 0.25
WEIGHT_ENGAGEMENT = 0.30

# SearXNG weights (no engagement data)
WEB_WEIGHT_RELEVANCE = 0.55
WEB_WEIGHT_RECENCY = 0.45
WEB_SOURCE_PENALTY = 15   # Default when query_type unknown

# Date confidence adjustments for web results
WEB_VERIFIED_BONUS = 10
WEB_NO_DATE_PENALTY = 20

DEFAULT_ENGAGEMENT = 35
UNKNOWN_ENGAGEMENT_PENALTY = 3


def log1p_safe(x: Optional[int]) -> float:
    """Safe log1p that handles None and negative values."""
    if x is None or x < 0:
        return 0.0
    return math.log1p(x)


def _compute_engagement_raw(eng: Optional[Engagement], source: str, top_comment_score: Optional[int] = None) -> Optional[float]:
    """Platform-specific raw engagement score.

    Returns None if no meaningful engagement data exists.
    """
    if eng is None:
        return None

    if source == "reddit":
        if eng.score is None and eng.num_comments is None:
            return None
        return (0.50 * log1p_safe(eng.score) +
                0.35 * log1p_safe(eng.num_comments) +
                0.05 * ((eng.upvote_ratio or 0.5) * 10) +
                0.10 * log1p_safe(top_comment_score))

    elif source == "x":
        if eng.likes is None and eng.reposts is None:
            return None
        return (0.55 * log1p_safe(eng.likes) +
                0.25 * log1p_safe(eng.reposts) +
                0.15 * log1p_safe(eng.replies) +
                0.05 * log1p_safe(eng.quotes))

    elif source == "youtube":
        if eng.views is None and eng.likes is None:
            return None
        return (0.50 * log1p_safe(eng.views) +
                0.35 * log1p_safe(eng.likes) +
                0.15 * log1p_safe(eng.num_comments))

    elif source == "hackernews":
        if eng.score is None and eng.num_comments is None:
            return None
        return (0.55 * log1p_safe(eng.score) +
                0.45 * log1p_safe(eng.num_comments))

    # searxng / unknown: no engagement
    return None


def normalize_to_100(values: List[Optional[float]], default: float = 50) -> List[Optional[float]]:
    """Normalize a list of values to 0-100 scale. None preserved."""
    valid = [v for v in values if v is not None]
    if not valid:
        return [default if v is None else 50 for v in values]

    min_val = min(valid)
    max_val = max(valid)
    range_val = max_val - min_val

    if range_val == 0:
        return [None if v is None else 50 for v in values]

    result = []
    for v in values:
        if v is None:
            result.append(None)
        else:
            result.append(((v - min_val) / range_val) * 100)
    return result


def score_items(items: List[SearchResult], query_type: QueryType = None, max_days: int = 30) -> List[SearchResult]:
    """Score a list of items from any single source.

    Handles both social platforms (with engagement) and web (without).
    Modifies items in-place and returns them.
    """
    if not items:
        return items

    source = items[0].source

    # Web/SearXNG: no engagement data
    if source == "searxng":
        return _score_web_items(items, query_type, max_days)

    # Social platforms: has engagement
    # Compute raw engagement per item
    eng_raw = []
    for item in items:
        top_cmt_score = None
        if source == "reddit" and hasattr(item, 'top_comments') and item.top_comments:
            top_cmt_score = item.top_comments[0].get("score") if isinstance(item.top_comments[0], dict) else None
        eng_raw.append(_compute_engagement_raw(item.engagement, source, top_cmt_score))

    # Normalize engagement to 0-100
    eng_normalized = normalize_to_100(eng_raw)

    for i, item in enumerate(items):
        rel_score = item.relevance * 100
        rec_score = dates.recency_score(item.date, max_days=max_days)

        if eng_normalized[i] is not None:
            eng_score = eng_normalized[i]
        else:
            eng_score = DEFAULT_ENGAGEMENT

        # Store subscores
        item.relevance = item.relevance  # keep raw 0-1
        item.recency = rec_score / 100.0
        item.engagement_score = eng_score / 100.0

        overall = (
            WEIGHT_RELEVANCE * rel_score +
            WEIGHT_RECENCY * rec_score +
            WEIGHT_ENGAGEMENT * eng_score
        )

        if eng_raw[i] is None:
            overall -= UNKNOWN_ENGAGEMENT_PENALTY

        if item.date_confidence == "low":
            overall -= 5
        elif item.date_confidence == "med":
            overall -= 2

        item.score = max(0.0, min(100.0, overall))

    return items


def _score_web_items(items: List[SearchResult], query_type: QueryType = None, max_days: int = 30) -> List[SearchResult]:
    """Score web/SearXNG results (no engagement data)."""
    penalty = WEBSEARCH_PENALTY_BY_TYPE.get(query_type, WEB_SOURCE_PENALTY) if query_type else WEB_SOURCE_PENALTY

    for item in items:
        rel_score = item.relevance * 100
        rec_score = dates.recency_score(item.date, max_days=max_days)

        item.recency = rec_score / 100.0
        item.engagement_score = 0.0

        overall = (
            WEB_WEIGHT_RELEVANCE * rel_score +
            WEB_WEIGHT_RECENCY * rec_score
        )
        overall -= penalty

        if item.date_confidence == "high":
            overall += WEB_VERIFIED_BONUS
        elif item.date_confidence == "low":
            overall -= WEB_NO_DATE_PENALTY

        item.score = max(0.0, min(100.0, overall))

    return items


def relevance_filter(items: List[SearchResult], source_name: str, threshold: float = 0.3) -> List[SearchResult]:
    """Filter items below relevance threshold with minimum-result guarantee.

    Lists with 3 or fewer items returned unchanged.
    If all below threshold, keeps top 3 by relevance.
    """
    if len(items) <= 3:
        return items
    passed = [i for i in items if i.relevance >= threshold]
    if not passed:
        print(f"[{source_name} WARNING] All results below relevance {threshold}, keeping top 3", file=sys.stderr)
        by_rel = sorted(items, key=lambda x: x.relevance, reverse=True)
        return by_rel[:3]
    return passed


def sort_all(items: List[SearchResult], query_type: QueryType = None) -> List[SearchResult]:
    """Sort items by score desc → date desc → source tiebreaker."""
    tiebreaker = TIEBREAKER_BY_TYPE.get(query_type) if query_type else None
    if not tiebreaker:
        tiebreaker = {"reddit": 0, "x": 1, "youtube": 2, "hn": 3, "searxng": 4}

    def sort_key(item):
        score = -item.score
        date_val = item.date or "0000-00-00"
        date_key = -int(date_val.replace("-", ""))
        source_priority = tiebreaker.get(item.source, 99)
        text = item.title or item.text or ""
        return (score, date_key, source_priority, text)

    return sorted(items, key=sort_key)
