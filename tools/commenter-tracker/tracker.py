#!/usr/bin/env python3
"""
commenter-pattern-tracker — detects repeated phrase spam, burst posting,
and low-substance comment patterns per account.

Part of M3 (quality filter) for the goon repo.

Usage:
  python3 tracker.py input.json              # pretty-print results
  python3 tracker.py input.json -o out.json  # write to file

Library:
  from tracker import analyze_comments
  result = analyze_comments({"comments": [...]})
"""

import json
import math
import os
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RULES_PATH = os.path.join(SCRIPT_DIR, "rules.json")

_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "]+",
    flags=re.UNICODE,
)


def load_rules(path=None):
    path = path or DEFAULT_RULES_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _tokenize(text):
    """Lowercase, strip emoji, split into word tokens."""
    cleaned = _EMOJI_RE.sub(" ", text)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned.lower())
    return [t for t in cleaned.split() if len(t) >= 2]


def _jaccard(tokens_a, tokens_b):
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    set_a, set_b = set(tokens_a), set(tokens_b)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _parse_timestamp(ts_str):
    """Parse ISO 8601 timestamp with or without timezone."""
    ts_str = ts_str.strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S%z",
    ):
        try:
            dt = datetime.strptime(ts_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Cannot parse timestamp: {ts_str}")


def _emoji_ratio(text):
    emoji_chars = sum(1 for c in text if unicodedata.category(c) in ("So", "Sk") or _EMOJI_RE.match(c))
    total = len(text.replace(" ", ""))
    if total == 0:
        return 0.0
    return emoji_chars / total


def _find_repeated_phrases(comments, rules):
    """Find near-duplicate and exact-duplicate phrases among an author's comments."""
    threshold = rules["phrase_similarity"]["jaccard_threshold"]
    tokenized = [_tokenize(c["text"]) for c in comments]
    repeated = []
    seen_pairs = set()

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            pair_key = (i, j)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            sim = _jaccard(tokenized[i], tokenized[j])
            if sim >= threshold:
                overlap_tokens = set(tokenized[i]) & set(tokenized[j])
                phrase = " ".join(sorted(overlap_tokens))
                if phrase and phrase not in repeated:
                    repeated.append(phrase)

    return repeated


def _find_burst_windows(comments, rules):
    """Find time windows where the author posted >= min_comments."""
    window_minutes = rules["burst_detection"]["window_minutes"]
    min_count = rules["burst_detection"]["min_comments_in_window"]

    timestamps = []
    for c in comments:
        try:
            timestamps.append(_parse_timestamp(c["timestamp"]))
        except (ValueError, KeyError):
            continue

    if len(timestamps) < min_count:
        return []

    timestamps.sort()
    window_delta = timedelta(minutes=window_minutes)

    bursts = []
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
            bursts.append(burst)
            i = j
        else:
            i += 1

    return bursts


def _is_low_substance(text, rules):
    """Check if a comment is low-substance: generic praise, emoji-heavy, promo, or very short."""
    ls_rules = rules["low_substance"]
    words = text.split()

    for pattern in ls_rules["generic_praise_patterns"]:
        if re.search(pattern, text):
            signal_found = False
            for sig_pattern in ls_rules["signal_terms"]:
                if re.search(sig_pattern, text):
                    signal_found = True
                    break
            if not signal_found:
                return True

    if len(words) <= ls_rules["short_comment_max_words"]:
        if _emoji_ratio(text) >= ls_rules["emoji_ratio_threshold"]:
            return True
        stripped = _EMOJI_RE.sub("", text).strip()
        stripped = re.sub(r"[!?.]+", "", stripped).strip()
        remaining_words = [w for w in stripped.split() if len(w) >= 2]
        if len(remaining_words) <= 2:
            return True

    if _emoji_ratio(text) >= ls_rules["emoji_ratio_threshold"]:
        signal_found = any(re.search(p, text) for p in ls_rules["signal_terms"])
        if not signal_found:
            return True

    for pattern in rules.get("thread_hijack_patterns", []):
        if re.search(pattern, text):
            signal_found = any(re.search(p, text) for p in ls_rules["signal_terms"])
            if not signal_found:
                return True

    for pattern in rules.get("service_manifest_patterns", []):
        if re.search(pattern, text):
            signal_found = any(re.search(p, text) for p in ls_rules["signal_terms"])
            if not signal_found:
                return True

    return False


def _generic_praise_density(text, rules):
    """Return a 0-1 score for how noise-dense the text is (praise, promo, solicitation)."""
    ls_rules = rules["low_substance"]
    matches = 0
    for pattern in ls_rules["generic_praise_patterns"]:
        matches += len(re.findall(pattern, text))

    for pattern in rules.get("thread_hijack_patterns", []):
        matches += len(re.findall(pattern, text))

    for pattern in rules.get("service_manifest_patterns", []):
        matches += len(re.findall(pattern, text))

    excl_count = text.count("!")
    emoji_count = len(_EMOJI_RE.findall(text))

    words = text.split()
    word_count = max(len(words), 1)

    raw = (matches * 2 + excl_count + emoji_count) / word_count
    return min(raw, 1.0)


def _compute_spam_score(author_data, rules):
    """
    Combine per-account metrics into a single 0-1 spam_score.

    Components:
    - repeated_phrase_ratio: fraction of comments that are near-duplicates
    - burst_ratio: fraction of comments inside burst windows
    - low_substance_ratio: fraction of low-substance comments
    - post_spread_factor: high distinct-post count in short time
    - generic_praise_density: average praise/emoji density across comments
    """
    weights = rules["spam_score_weights"]
    comments = author_data["comments"]
    n = len(comments)
    if n == 0:
        return 0.0

    tokenized = [_tokenize(c["text"]) for c in comments]
    threshold = rules["phrase_similarity"]["jaccard_threshold"]
    dup_flags = [False] * n
    for i in range(n):
        for j in range(i + 1, n):
            if _jaccard(tokenized[i], tokenized[j]) >= threshold:
                dup_flags[i] = True
                dup_flags[j] = True
    repeated_phrase_ratio = sum(dup_flags) / n

    burst_comment_count = sum(b["count"] for b in author_data["burst_windows"])
    burst_ratio = min(burst_comment_count / n, 1.0)

    low_sub_count = sum(1 for c in comments if _is_low_substance(c["text"], rules))
    low_substance_ratio = low_sub_count / n

    unique_posts = len(set(c.get("post_url", "") for c in comments))
    spread_rules = rules["post_spread"]
    if unique_posts >= spread_rules["high_spread_threshold"]:
        timestamps = []
        for c in comments:
            try:
                timestamps.append(_parse_timestamp(c["timestamp"]))
            except (ValueError, KeyError):
                continue
        if len(timestamps) >= 2:
            time_span = (max(timestamps) - min(timestamps)).total_seconds() / 3600.0
            if time_span <= spread_rules["time_window_hours"]:
                post_spread_factor = min(unique_posts / (spread_rules["high_spread_threshold"] + 2), 1.0)
            else:
                post_spread_factor = max(0, min((unique_posts / max(time_span * 4, 1)) - 0.2, 1.0))
        else:
            post_spread_factor = 0.5 if unique_posts >= spread_rules["high_spread_threshold"] else 0.0
    else:
        post_spread_factor = 0.0

    avg_praise = sum(_generic_praise_density(c["text"], rules) for c in comments) / n

    raw_score = (
        weights["repeated_phrase_ratio"] * repeated_phrase_ratio
        + weights["burst_ratio"] * burst_ratio
        + weights["low_substance_ratio"] * low_substance_ratio
        + weights["post_spread_factor"] * post_spread_factor
        + weights["generic_praise_density"] * avg_praise
    )

    return round(min(max(raw_score, 0.0), 1.0), 4)


def analyze_comments(data, rules=None):
    """
    Analyze a batch of comments and return per-account spam metrics.

    Args:
        data: dict with "comments" key containing list of comment dicts
        rules: optional rules dict (loaded from rules.json if None)

    Returns:
        dict with "accounts" key containing list of per-account result dicts
    """
    if rules is None:
        rules = load_rules()

    comments = data.get("comments", [])
    if not comments:
        return {"accounts": []}

    by_author = defaultdict(list)
    for c in comments:
        author = c.get("author", "unknown")
        by_author[author].append(c)

    accounts = []
    for author, author_comments in by_author.items():
        repeated_phrases = _find_repeated_phrases(author_comments, rules)
        burst_windows = _find_burst_windows(author_comments, rules)
        touched_posts = list(set(c.get("post_url", "") for c in author_comments if c.get("post_url")))

        author_data = {
            "comments": author_comments,
            "repeated_phrases": repeated_phrases,
            "burst_windows": burst_windows,
            "touched_posts": touched_posts,
        }

        spam_score = _compute_spam_score(author_data, rules)

        accounts.append({
            "author": author,
            "comment_count": len(author_comments),
            "repeated_phrases": repeated_phrases,
            "touched_posts": touched_posts,
            "burst_windows": burst_windows,
            "spam_score": spam_score,
        })

    accounts.sort(key=lambda a: a["spam_score"], reverse=True)
    return {"accounts": accounts}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tracker.py <input.json> [-o output.json]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = analyze_comments(data)
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"Results written to {output_path}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
