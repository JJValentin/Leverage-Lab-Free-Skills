# Derived from last30days v2.9.5 by Matt Van Horn (MIT License)
# https://github.com/mattvanhorn/last30days
# Adapted for deep-search schema

"""YouTube search and transcript extraction via yt-dlp. No API key needed."""

import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.schema import YouTubeResult, Engagement
from lib.relevance import token_overlap_relevance
from lib.query import extract_core_subject
from lib.dates import get_date_range

# Depth config
DEPTH_CONFIG = {"quick": 10, "default": 20, "deep": 40}
TRANSCRIPT_LIMITS = {"quick": 3, "default": 5, "deep": 8}
TRANSCRIPT_MAX_WORDS = 5000

# YouTube-specific noise set (keeps content-type words like tutorial, review, tips)
_YT_NOISE = frozenset({
    'best', 'top', 'good', 'great', 'awesome', 'killer',
    'latest', 'new', 'news', 'update', 'updates',
    'trending', 'hottest', 'popular', 'viral',
    'practices', 'features', 'recommendations', 'advice',
    'prompt', 'prompts', 'prompting',
    'methods', 'strategies', 'approaches',
})


def _log(msg: str):
    sys.stderr.write(f"[YouTube] {msg}\n")
    sys.stderr.flush()


def _yt_core_subject(topic: str) -> str:
    return extract_core_subject(topic, noise=_YT_NOISE)


def extract_transcript_highlights(transcript: str, topic: str, limit: int = 5) -> List[str]:
    """Extract quotable highlights from a transcript."""
    if not transcript:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', transcript)
    filler = [
        r"^(hey |hi |what's up|welcome back|in today's video|don't forget to)",
        r"(subscribe|like and comment|hit the bell|check out the link|down below)",
        r"^(so |and |but |okay |alright |um |uh )",
        r"(thanks for watching|see you (next|in the)|bye)",
    ]
    topic_words = [w.lower() for w in topic.lower().split() if len(w) > 2]
    candidates = []
    for sent in sentences:
        sent = sent.strip()
        words = sent.split()
        if len(words) < 8 or len(words) > 50:
            continue
        if any(re.search(p, sent, re.IGNORECASE) for p in filler):
            continue
        score = 0
        if re.search(r'\d', sent):
            score += 2
        if re.search(r'[A-Z][a-z]+', sent):
            score += 1
        if '?' in sent:
            score += 1
        sent_lower = sent.lower()
        if any(w in sent_lower for w in topic_words):
            score += 2
        candidates.append((score, sent))
    candidates.sort(key=lambda x: -x[0])
    return [sent for _, sent in candidates[:limit]]


def _clean_vtt(vtt_text: str) -> str:
    """Convert VTT subtitle format to clean plaintext."""
    text = re.sub(r'^WEBVTT.*?\n\n', '', vtt_text, flags=re.DOTALL)
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    lines = text.strip().split('\n')
    seen = set()
    unique = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            unique.append(stripped)
    return re.sub(r'\s+', ' ', ' '.join(unique)).strip()


def fetch_transcript(video_id: str, temp_dir: str) -> Optional[str]:
    """Fetch auto-generated transcript for a video."""
    cmd = [
        "yt-dlp", "--ignore-config", "--no-cookies-from-browser",
        "--write-auto-subs", "--sub-lang", "en", "--sub-format", "vtt",
        "--skip-download", "--no-warnings",
        "-o", f"{temp_dir}/%(id)s",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    preexec = os.setsid if hasattr(os, 'setsid') else None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=preexec)
        try:
            proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                proc.kill()
            proc.wait(timeout=5)
            return None
    except FileNotFoundError:
        return None

    vtt_path = Path(temp_dir) / f"{video_id}.en.vtt"
    if not vtt_path.exists():
        for p in Path(temp_dir).glob(f"{video_id}*.vtt"):
            vtt_path = p
            break
        else:
            return None
    try:
        raw = vtt_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    transcript = _clean_vtt(raw)
    words = transcript.split()
    if len(words) > TRANSCRIPT_MAX_WORDS:
        transcript = ' '.join(words[:TRANSCRIPT_MAX_WORDS]) + '...'
    return transcript if transcript else None


def fetch_transcripts_parallel(video_ids: List[str], max_workers: int = 5) -> Dict[str, Optional[str]]:
    """Fetch transcripts for multiple videos in parallel."""
    if not video_ids:
        return {}
    _log(f"Fetching transcripts for {len(video_ids)} videos")
    results = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_transcript, vid, temp_dir): vid for vid in video_ids}
            for future in as_completed(futures):
                vid = futures[future]
                try:
                    results[vid] = future.result()
                except Exception:
                    results[vid] = None
    got = sum(1 for v in results.values() if v)
    _log(f"Got transcripts for {got}/{len(video_ids)} videos")
    return results


def search(topic: str, from_date: str, to_date: str, depth: str = "default", transcripts: bool = True) -> List[YouTubeResult]:
    """Search YouTube and return YouTubeResult objects.

    Args:
        topic: Search topic
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        depth: quick/default/deep
        transcripts: Whether to fetch transcripts for top results

    Returns:
        List of YouTubeResult
    """
    if not shutil.which("yt-dlp"):
        _log("yt-dlp not installed")
        return []

    count = DEPTH_CONFIG.get(depth, 20)
    core_topic = _yt_core_subject(topic)
    _log(f"Searching for '{core_topic}' (since {from_date}, count={count})")

    cmd = [
        "yt-dlp", "--ignore-config", "--no-cookies-from-browser",
        f"ytsearch{count}:{core_topic}",
        "--dump-json", "--no-warnings", "--no-download",
    ]
    preexec = os.setsid if hasattr(os, 'setsid') else None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=preexec)
        try:
            stdout, stderr = proc.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                proc.kill()
            proc.wait(timeout=5)
            _log("Search timed out (120s)")
            return []
    except FileNotFoundError:
        return []

    if not (stdout or "").strip():
        _log("Search returned 0 results")
        return []

    # Parse results
    results = []
    for i, line in enumerate(stdout.strip().split("\n")):
        line = line.strip()
        if not line:
            continue
        try:
            video = json.loads(line)
        except json.JSONDecodeError:
            continue

        video_id = video.get("id", "")
        upload_date = video.get("upload_date", "")
        date_str = None
        if upload_date and len(upload_date) == 8:
            date_str = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"

        results.append(YouTubeResult(
            id=f"YT{i+1}",
            title=video.get("title", ""),
            url=f"https://www.youtube.com/watch?v={video_id}",
            date=date_str,
            date_confidence="high" if date_str else "low",
            channel_name=video.get("channel", video.get("uploader", "")),
            duration=video.get("duration"),
            engagement=Engagement(
                views=video.get("view_count") or 0,
                likes=video.get("like_count") or 0,
                num_comments=video.get("comment_count") or 0,
            ),
            relevance=token_overlap_relevance(core_topic, video.get("title", "")),
            why_relevant=f"YouTube: {video.get('title', core_topic)[:60]}",
            extra={"video_id": video_id},
        ))

    # Soft date filter
    recent = [r for r in results if r.date and r.date >= from_date]
    if len(recent) >= 3:
        results = recent
        _log(f"Found {len(results)} videos within date range")
    else:
        _log(f"Found {len(results)} videos ({len(recent)} within date range, keeping all)")

    # Sort by views
    results.sort(key=lambda r: r.engagement.views or 0, reverse=True)

    # Fetch transcripts for top results
    if transcripts and results:
        transcript_limit = TRANSCRIPT_LIMITS.get(depth, 5)
        top_ids = [r.extra["video_id"] for r in results[:transcript_limit]]
        transcript_data = fetch_transcripts_parallel(top_ids)

        for r in results:
            vid = r.extra.get("video_id", "")
            t = transcript_data.get(vid)
            r.transcript_snippet = t or ""
            r.highlights = extract_transcript_highlights(t or "", core_topic)

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube deep-search")
    parser.add_argument("topic", help="Search topic")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument("--depth", default="default", choices=["quick", "default", "deep"])
    parser.add_argument("--no-transcripts", action="store_true")
    args = parser.parse_args()

    from_date, to_date = get_date_range(args.days)
    results = search(args.topic, from_date, to_date, args.depth, transcripts=not args.no_transcripts)

    for r in results:
        has_t = "📝" if r.transcript_snippet else "  "
        print(f"{has_t} [{r.date or '????'}] {r.title} ({r.engagement.views:,} views) rel={r.relevance:.2f}")
        if r.highlights:
            for h in r.highlights[:2]:
                print(f"    💡 {h[:120]}")
    print(f"\n{len(results)} results")
