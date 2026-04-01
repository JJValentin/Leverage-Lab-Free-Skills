# Derived from last30days v2.9.5 by Matt Van Horn (MIT License)
# https://github.com/mattvanhorn/last30days
# Simplified to dataclasses for deep-search

"""Shared data models for deep-search."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Engagement:
    """Platform-agnostic engagement metrics. All fields optional."""
    likes: Optional[int] = None
    reposts: Optional[int] = None
    replies: Optional[int] = None
    quotes: Optional[int] = None
    views: Optional[int] = None
    score: Optional[int] = None          # Reddit score / HN points
    num_comments: Optional[int] = None
    upvote_ratio: Optional[float] = None  # Reddit-specific


@dataclass
class SearchResult:
    """Base search result from any platform."""
    id: str = ""
    title: str = ""
    text: str = ""
    url: str = ""
    date: Optional[str] = None           # YYYY-MM-DD
    date_confidence: str = "low"         # high / med / low
    source: str = ""                     # youtube / hackernews / reddit / x / searxng
    engagement: Engagement = field(default_factory=Engagement)
    relevance: float = 0.0              # 0.0-1.0 from relevance scorer
    recency: float = 0.0               # 0.0-1.0 from recency scorer
    engagement_score: float = 0.0       # 0.0-1.0 normalized engagement
    score: float = 0.0                  # 0-100 composite score
    cross_refs: List[str] = field(default_factory=list)  # IDs of related items from other sources
    why_relevant: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)  # Platform-specific overflow

    # Platform-specific fields (set by subclass or via extra)
    # YouTube: transcript_snippet, channel_name, duration
    # Reddit: subreddit, selftext, top_comments, comment_insights
    # X: author_handle, author_name
    # HN: story_url, top_comments
    # SearXNG: engine, snippet


@dataclass
class YouTubeResult(SearchResult):
    """YouTube search result with transcript data."""
    source: str = "youtube"
    channel_name: str = ""
    duration: Optional[int] = None       # seconds
    transcript_snippet: str = ""
    highlights: List[str] = field(default_factory=list)


@dataclass
class HackerNewsResult(SearchResult):
    """HN search result with comment data."""
    source: str = "hackernews"
    story_url: str = ""                  # external URL (vs HN discussion URL)
    top_comments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RedditResult(SearchResult):
    """Reddit search result with community context."""
    source: str = "reddit"
    subreddit: str = ""
    selftext: str = ""
    top_comments: List[Dict[str, Any]] = field(default_factory=list)
    comment_insights: List[str] = field(default_factory=list)


@dataclass
class XResult(SearchResult):
    """X/Twitter search result."""
    source: str = "x"
    author_handle: str = ""
    author_name: str = ""


@dataclass
class SearXNGResult(SearchResult):
    """Web search result from SearXNG."""
    source: str = "searxng"
    engine: str = ""
    snippet: str = ""
