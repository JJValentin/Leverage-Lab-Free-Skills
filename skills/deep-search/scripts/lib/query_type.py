# Derived from last30days v2.9.5 by Matt Van Horn (MIT License)
# https://github.com/mattvanhorn/last30days
# Adapted: removed Polymarket/TruthSocial/TikTok/Instagram/Bluesky, added SearXNG

"""Query type detection for source selection and scoring adjustments."""

import re
from typing import Literal

QueryType = Literal["product", "concept", "opinion", "how_to", "comparison", "breaking_news"]

# Pattern-based classification (no LLM, no external deps)
_PRODUCT_PATTERNS = re.compile(
    r"\b(price|pricing|cost|buy|purchase|deal|discount|subscription|plan|tier|free tier|alternative|prompt|prompts|prompting|template|templates)\b", re.I
)
_CONCEPT_PATTERNS = re.compile(
    r"\b(what is|what are|explain|definition|how does|how do|overview|introduction|guide to|primer)\b", re.I
)
_OPINION_PATTERNS = re.compile(
    r"\b(worth it|thoughts on|opinion|review|experience with|recommend|should i|pros and cons|good or bad)\b", re.I
)
_HOWTO_PATTERNS = re.compile(
    r"\b(how to|tutorial|step by step|setup|install|configure|deploy|migrate|implement|build a|create a|prompting|prompts?|best practices|tips|examples|animation|animations|video workflow|render pipeline)\b",
    re.I,
)
_COMPARISON_PATTERNS = re.compile(
    r"\b(vs\.?|versus|compared to|comparison|better than|difference between|switch from)\b", re.I
)
_BREAKING_PATTERNS = re.compile(
    r"\b(latest|breaking|just announced|launched|released|new|update|news|happened|today|this week)\b", re.I
)


def detect_query_type(topic: str) -> QueryType:
    """Classify a query into a type using pattern matching.

    Returns the first match in priority order.
    """
    if _COMPARISON_PATTERNS.search(topic):
        return "comparison"
    if _HOWTO_PATTERNS.search(topic):
        return "how_to"
    if _PRODUCT_PATTERNS.search(topic):
        return "product"
    if _OPINION_PATTERNS.search(topic):
        return "opinion"
    if _CONCEPT_PATTERNS.search(topic):
        return "concept"
    if _BREAKING_PATTERNS.search(topic):
        return "breaking_news"

    # Default: breaking_news (most common for "what's happening with X")
    return "breaking_news"


# Source tiering by query type.
# Tier 1: always run. Tier 2: run if available. Tier 3: opt-in only.
# Available platforms: reddit, x, youtube, hackernews (hn), searxng
SOURCE_TIERS = {
    "product":       {"tier1": {"reddit", "x", "youtube"},    "tier2": {"searxng", "hn"}},
    "concept":       {"tier1": {"reddit", "hn", "searxng"},   "tier2": {"youtube", "x"}},
    "opinion":       {"tier1": {"reddit", "x"},               "tier2": {"youtube", "hn"}},
    "how_to":        {"tier1": {"youtube", "reddit", "hn"},   "tier2": {"searxng", "x"}},
    "comparison":    {"tier1": {"reddit", "hn", "youtube"},   "tier2": {"x", "searxng"}},
    "breaking_news": {"tier1": {"x", "reddit", "searxng"},    "tier2": {"hn", "youtube"}},
}

# SearXNG penalty by query type (0-15 scale).
# Lower = SearXNG results more valuable for this query type.
WEBSEARCH_PENALTY_BY_TYPE = {
    "product": 15,        # social discussion > blog posts
    "concept": 0,         # web docs are authoritative
    "opinion": 15,        # social discussion > blog posts
    "how_to": 5,          # tutorials on web are valuable
    "comparison": 10,     # mix of social and web
    "breaking_news": 10,  # news sites are valuable
}

# Tiebreaker priority by query type (lower = higher priority).
TIEBREAKER_BY_TYPE = {
    "product":       {"reddit": 0, "x": 1, "youtube": 2, "hn": 3, "searxng": 4},
    "concept":       {"hn": 0, "reddit": 1, "searxng": 2, "youtube": 3, "x": 4},
    "opinion":       {"reddit": 0, "x": 1, "youtube": 2, "hn": 3, "searxng": 4},
    "how_to":        {"youtube": 0, "reddit": 1, "hn": 2, "searxng": 3, "x": 4},
    "comparison":    {"reddit": 0, "hn": 1, "youtube": 2, "x": 3, "searxng": 4},
    "breaking_news": {"x": 0, "reddit": 1, "searxng": 2, "hn": 3, "youtube": 4},
}


def is_source_enabled(source: str, query_type: QueryType, explicitly_requested: bool = False) -> bool:
    """Check if a source should run for a given query type."""
    if explicitly_requested:
        return True
    tiers = SOURCE_TIERS.get(query_type, SOURCE_TIERS["breaking_news"])
    return source in tiers["tier1"] or source in tiers["tier2"]
