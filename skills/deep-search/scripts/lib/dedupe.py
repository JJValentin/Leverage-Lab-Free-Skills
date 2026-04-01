# Derived from last30days v2.9.5 by Matt Van Horn (MIT License)
# https://github.com/mattvanhorn/last30days
# Adapted for deep-search simplified schema

"""Near-duplicate detection and cross-source convergence linking."""

import re
from typing import List, Set, Tuple

from .schema import SearchResult

# Stopwords for token-based Jaccard
STOPWORDS = frozenset({
    'the', 'a', 'an', 'to', 'for', 'how', 'is', 'in', 'of', 'on',
    'and', 'with', 'from', 'by', 'at', 'this', 'that', 'it', 'my',
    'your', 'i', 'me', 'we', 'you', 'what', 'are', 'do', 'can',
    'its', 'be', 'or', 'not', 'no', 'so', 'if', 'but', 'about',
    'all', 'just', 'get', 'has', 'have', 'was', 'will', 'show', 'hn',
})


def normalize_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_ngrams(text: str, n: int = 3) -> Set[str]:
    """Get character n-grams from text."""
    text = normalize_text(text)
    if len(text) < n:
        return {text}
    return {text[i:i+n] for i in range(len(text) - n + 1)}


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def _tokenize(text: str) -> Set[str]:
    """Tokenize for cross-source comparison."""
    words = re.sub(r'[^\w\s]', ' ', text.lower()).split()
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _token_jaccard(text_a: str, text_b: str) -> float:
    """Token-level Jaccard similarity."""
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union else 0.0


def _hybrid_similarity(text_a: str, text_b: str) -> float:
    """Max of char-trigram Jaccard and token Jaccard."""
    trigram_sim = jaccard_similarity(get_ngrams(text_a), get_ngrams(text_b))
    token_sim = _token_jaccard(text_a, text_b)
    return max(trigram_sim, token_sim)


def get_item_text(item: SearchResult) -> str:
    """Get the primary comparable text from an item."""
    if item.title:
        return item.title
    return item.text[:150] if item.text else ""


def _get_cross_source_text(item: SearchResult) -> str:
    """Get text for cross-source comparison. Truncates long texts for fairness."""
    # X/social posts: truncate to level playing field against short titles
    if item.source in ("x", "searxng"):
        text = item.text or item.title
        return text[:100]
    # HN: strip prefix
    if item.source == "hackernews":
        title = item.title
        for prefix in ("Show HN:", "Ask HN:", "Tell HN:"):
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        return title
    return get_item_text(item)


def find_duplicates(
    items: List[SearchResult],
    threshold: float = 0.7,
) -> List[Tuple[int, int]]:
    """Find near-duplicate pairs. Returns (i, j) index pairs."""
    duplicates = []
    ngrams = [get_ngrams(get_item_text(item)) for item in items]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            similarity = jaccard_similarity(ngrams[i], ngrams[j])
            if similarity >= threshold:
                duplicates.append((i, j))
    return duplicates


def dedupe_items(
    items: List[SearchResult],
    threshold: float = 0.7,
) -> List[SearchResult]:
    """Remove near-duplicates within a single source, keeping highest-scored.

    Items should be pre-sorted by score descending.
    """
    if len(items) <= 1:
        return items

    dup_pairs = find_duplicates(items, threshold)
    to_remove = set()
    for i, j in dup_pairs:
        if items[i].score >= items[j].score:
            to_remove.add(j)
        else:
            to_remove.add(i)

    return [item for idx, item in enumerate(items) if idx not in to_remove]


def cross_source_link(
    *source_lists: List[SearchResult],
    threshold: float = 0.40,
) -> None:
    """Annotate items with cross-source references (bidirectional).

    Compares items across different sources using hybrid similarity.
    When similarity exceeds threshold, adds bidirectional cross_refs.
    Modifies items in-place.
    """
    all_items = []
    for source_list in source_lists:
        all_items.extend(source_list)

    if len(all_items) <= 1:
        return

    texts = [_get_cross_source_text(item) for item in all_items]

    for i in range(len(all_items)):
        for j in range(i + 1, len(all_items)):
            # Skip same-source (handled by per-source dedupe)
            if all_items[i].source == all_items[j].source:
                continue

            similarity = _hybrid_similarity(texts[i], texts[j])
            if similarity >= threshold:
                if all_items[j].id not in all_items[i].cross_refs:
                    all_items[i].cross_refs.append(all_items[j].id)
                if all_items[i].id not in all_items[j].cross_refs:
                    all_items[j].cross_refs.append(all_items[i].id)
