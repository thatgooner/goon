"""
Moltbook commenter pattern tracker.

Detects repeated commenter spam, phrase reuse, burst posting, and coordinated
reply sludge that single-post scoring misses.

No external dependencies — stdlib only.

Usage:
    from tracker import analyze
    result = analyze({"comments": [
        {"author": "bot", "text": "Amazing!", "post_url": "https://...", "timestamp": "2026-03-13T02:00:00Z"}
    ]})
"""

import json
import math
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

_RULES_PATH = Path(__file__).parent / "rules.json"
_rules_cache: Optional[dict] = None


def _load_rules(path: Optional[str] = None) -> dict:
    global _rules_cache
    if _rules_cache is not None and path is None:
        return _rules_cache
    p = Path(path) if path else _RULES_PATH
    with open(p, "r", encoding="utf-8") as f:
        rules = json.load(f)
    if path is None:
        _rules_cache = rules
    return rules


def _reload_rules():
    global _rules_cache
    _rules_cache = None
    return _load_rules()


# ---------------------------------------------------------------------------
# Timestamp parsing
# ---------------------------------------------------------------------------

_TS_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S%z",
]


def _parse_ts(ts_str: str) -> Optional[datetime]:
    for fmt in _TS_FORMATS:
        try:
            dt = datetime.strptime(ts_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Phrase similarity (no external deps — simple token overlap)
# ---------------------------------------------------------------------------

_STOP_WORDS = frozenset([
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "about", "this",
    "that", "it", "its", "and", "or", "but", "if", "so", "not", "no",
    "i", "you", "we", "they", "he", "she", "me", "my", "your", "our",
])

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list:
    tokens = _WORD_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]


def _token_similarity(tokens_a: list, tokens_b: list) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    set_a, set_b = set(tokens_a), set(tokens_b)
    intersection = set_a & set_b
    union = set_a | set_b
    if not union:
        return 0.0
    return len(intersection) / len(union)


def _normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip().lower())
    text = re.sub(r"[^\w\s]", "", text)
    return text


# ---------------------------------------------------------------------------
# Pattern detection
# ---------------------------------------------------------------------------

def _find_repeated_phrases(comments: list, threshold: float) -> list:
    """Find phrases repeated across 2+ comments from the same author."""
    repeated = []
    n = len(comments)
    if n < 2:
        return repeated

    normalized = [_normalize_text(c["text"]) for c in comments]
    tokenized = [_tokenize(c["text"]) for c in comments]
    seen_pairs = set()

    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in seen_pairs:
                continue
            seen_pairs.add((i, j))

            if normalized[i] == normalized[j]:
                phrase = comments[i]["text"].strip()[:100]
                if phrase not in repeated:
                    repeated.append(phrase)
                continue

            sim = _token_similarity(tokenized[i], tokenized[j])
            if sim >= threshold:
                phrase = comments[i]["text"].strip()[:100]
                if phrase not in repeated:
                    repeated.append(phrase)

    return repeated


def _find_burst_windows(comments: list, window_minutes: int, min_count: int) -> list:
    """Find time windows where an author posted many comments quickly."""
    timestamps = []
    for c in comments:
        ts_str = c.get("timestamp", "")
        if ts_str:
            ts = _parse_ts(ts_str)
            if ts:
                timestamps.append(ts)
    timestamps.sort()

    if len(timestamps) < min_count:
        return []

    bursts = []
    window_delta = timedelta(minutes=window_minutes)

    i = 0
    while i < len(timestamps):
        window_end = timestamps[i] + window_delta
        j = i
        while j < len(timestamps) and timestamps[j] <= window_end:
            j += 1

        count = j - i
        if count >= min_count:
            burst = {
                "start": timestamps[i].isoformat(),
                "end": timestamps[j - 1].isoformat(),
                "count": count,
            }
            if not bursts or bursts[-1]["start"] != burst["start"]:
                bursts.append(burst)
            i = j
        else:
            i += 1

    return bursts


def _check_patterns(text: str, patterns: list) -> bool:
    for pat in patterns:
        try:
            if re.search(pat, text):
                return True
        except re.error:
            continue
    return False


def _substance_score(text: str, rules: dict) -> float:
    """0.0 = no substance, 1.0 = high substance."""
    indicators = rules.get("substance_indicators", [])
    hits = 0
    for pat in indicators:
        try:
            if re.search(pat, text):
                hits += 1
        except re.error:
            continue

    word_count = len(text.split())
    length_bonus = min(word_count / 100.0, 0.3)

    return min(1.0, (hits / max(len(indicators), 1)) * 0.7 + length_bonus)


# ---------------------------------------------------------------------------
# Spam score calculation
# ---------------------------------------------------------------------------

def _compute_spam_score(
    author: str,
    comments: list,
    repeated_phrases: list,
    burst_windows: list,
    touched_posts: list,
    rules: dict,
) -> float:
    weights = rules.get("scoring_weights", {})
    w_repeat = weights.get("repeated_phrases", 0.30)
    w_burst = weights.get("burst_activity", 0.25)
    w_substance = weights.get("low_substance", 0.20)
    w_spread = weights.get("post_spread", 0.15)
    w_praise = weights.get("generic_praise", 0.10)

    n_comments = len(comments)
    if n_comments == 0:
        return 0.0

    # --- Repeated phrase score ---
    repeat_ratio = len(repeated_phrases) / max(n_comments - 1, 1)
    repeat_score = min(1.0, repeat_ratio * 1.5)

    # --- Burst score ---
    if burst_windows:
        max_burst = max(b["count"] for b in burst_windows)
        burst_score = min(1.0, max_burst / max(n_comments, 5) * 1.5)
    else:
        burst_score = 0.0

    # --- Substance score (inverted: low substance = high spam score) ---
    avg_substance = 0.0
    for c in comments:
        avg_substance += _substance_score(c["text"], rules)
    avg_substance /= n_comments
    substance_spam = 1.0 - avg_substance

    # --- Post spread score ---
    # Many different posts touched in short time = suspicious
    n_posts = len(touched_posts)
    if n_posts > 1 and burst_windows:
        spread_score = min(1.0, n_posts / max(n_comments, 3) * (1.0 + len(burst_windows) * 0.3))
    elif n_posts > 3:
        spread_score = min(1.0, n_posts / 10.0)
    else:
        spread_score = 0.0

    # --- Generic praise score ---
    praise_patterns = rules.get("generic_praise_patterns", [])
    promo_patterns = rules.get("promo_patterns", [])
    meta_patterns = rules.get("meta_question_patterns", [])
    praise_count = 0
    promo_count = 0
    meta_count = 0
    for c in comments:
        if _check_patterns(c["text"], praise_patterns):
            praise_count += 1
        if _check_patterns(c["text"], promo_patterns):
            promo_count += 1
        if _check_patterns(c["text"], meta_patterns):
            meta_count += 1

    praise_ratio = praise_count / n_comments
    promo_ratio = promo_count / n_comments
    meta_ratio = meta_count / n_comments

    praise_score = min(1.0, praise_ratio * 1.2 + promo_ratio * 0.8 + meta_ratio * 0.5)

    raw_score = (
        w_repeat * repeat_score
        + w_burst * burst_score
        + w_substance * substance_spam
        + w_spread * spread_score
        + w_praise * praise_score
    )

    # Boost for extreme patterns
    if repeat_score > 0.8 and burst_score > 0.5:
        raw_score = min(1.0, raw_score * 1.3)
    if praise_ratio > 0.8 and n_comments >= 3:
        raw_score = min(1.0, raw_score * 1.2)
    if promo_ratio > 0.5:
        raw_score = min(1.0, raw_score + 0.15)

    # Dampen for accounts with real substance
    if avg_substance > 0.5 and repeat_score < 0.3:
        raw_score *= 0.6

    return round(min(1.0, max(0.0, raw_score)), 3)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze(data: dict, rules_path: Optional[str] = None) -> dict:
    """
    Analyze comment patterns across accounts.

    Args:
        data: {"comments": [{"author": str, "text": str, "post_url": str, "timestamp": str}]}
        rules_path: optional path to custom rules.json

    Returns:
        {
            "accounts": [{
                "author": str,
                "comment_count": int,
                "repeated_phrases": [str],
                "touched_posts": [str],
                "burst_windows": [{"start": str, "end": str, "count": int}],
                "spam_score": float 0-1
            }]
        }
    """
    rules = _load_rules(rules_path)
    comments = data.get("comments", [])

    by_author = defaultdict(list)
    for c in comments:
        author = c.get("author", "unknown")
        by_author[author].append(c)

    threshold = rules.get("phrase_similarity_threshold", 0.85)
    window_min = rules.get("burst_window_minutes", 15)
    burst_min = rules.get("burst_min_count", 3)

    accounts = []
    for author, author_comments in by_author.items():
        touched_posts = list(set(c.get("post_url", "") for c in author_comments if c.get("post_url")))

        repeated = _find_repeated_phrases(author_comments, threshold)
        bursts = _find_burst_windows(author_comments, window_min, burst_min)

        spam_score = _compute_spam_score(
            author, author_comments, repeated, bursts, touched_posts, rules
        )

        accounts.append({
            "author": author,
            "comment_count": len(author_comments),
            "repeated_phrases": repeated,
            "touched_posts": touched_posts,
            "burst_windows": bursts,
            "spam_score": spam_score,
        })

    accounts.sort(key=lambda a: a["spam_score"], reverse=True)

    return {"accounts": accounts}


def analyze_batch(data_list: list, rules_path: Optional[str] = None) -> list:
    return [analyze(d, rules_path) for d in data_list]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        with open(input_path, "r") as f:
            data = json.load(f)
        result = analyze(data)
        print(json.dumps(result, indent=2))
    else:
        sample = {
            "comments": [
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:02:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:05:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/5", "timestamp": "2026-03-13T02:08:00Z"},
                {"author": "legit_builder", "text": "I tested this against the polymarket CLOB API — the spread filter at 20% catches most illiquid markets. Here's my fork: github.com/legit/pm-filter", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "legit_builder", "text": "The funding rate divergence strategy needs a different approach for sub-$50k markets. I ran backtests on 200 markets and the win rate drops below 40% when volume is under 10k. Repo: github.com/legit/funding-bt", "post_url": "https://moltbook.com/post/6", "timestamp": "2026-03-15T14:30:00Z"},
            ]
        }
        result = analyze(sample)
        print(json.dumps(result, indent=2))
