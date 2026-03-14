"""
Search collision reducer for Moltbook keyword search.

Downranks results that matched only because the search term overlaps
with the author's username or a generic token in the text, and penalizes
repeated already-seen authors.
"""

import json
import os
import re
import sys
from typing import Any


RULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules.json")


def load_rules(path: str | None = None) -> dict:
    with open(path or RULES_PATH, "r") as f:
        return json.load(f)


def tokenize_query(query: str, stop_words: list[str]) -> list[str]:
    """Split query into significant tokens, lowercased, skipping stop words."""
    raw = re.split(r"[\s\-_./]+", query.lower())
    return [t for t in raw if t and t not in stop_words]


def tokenize_username(author: str) -> list[str]:
    """Split a username into tokens using common separators."""
    return [t.lower() for t in re.split(r"[\s\-_./]+", author) if t]


def _normalize(text: str) -> str:
    return text.lower()


def _token_in_username(token: str, author_tokens: list[str],
                       author_lower: str, rules: dict) -> bool:
    """Check if a token matches the username via exact token or substring."""
    if token in author_tokens:
        return True
    cfg = rules.get("collision_detection", {})
    if cfg.get("enable_substring_match", True):
        min_len = cfg.get("min_token_length_for_substring", 3)
        if len(token) >= min_len and token in author_lower:
            return True
    return False


def compute_relevance(query: str, tokens: list[str], text: str,
                      link_targets: list[str], rules: dict) -> float:
    """Score how relevant the result body/links are to the query."""
    bonuses = rules["relevance_bonuses"]
    text_lower = _normalize(text)
    query_lower = _normalize(query)

    if query_lower in text_lower:
        return bonuses["exact_phrase_in_body"]

    for link in link_targets:
        if query_lower in _normalize(link):
            return bonuses["exact_phrase_in_links"]

    if not tokens:
        return bonuses["no_tokens_in_body"]

    body_hits = sum(1 for t in tokens if t in text_lower)
    link_hits = sum(
        1 for t in tokens
        if any(t in _normalize(lnk) for lnk in link_targets)
    )
    combined_hits = 0
    for t in tokens:
        if t in text_lower or any(t in _normalize(lnk) for lnk in link_targets):
            combined_hits += 1

    ratio = combined_hits / len(tokens)

    if ratio >= 1.0:
        return bonuses["all_tokens_in_body"]
    elif ratio >= 0.6:
        return bonuses["most_tokens_in_body"]
    elif ratio > 0:
        return bonuses["some_tokens_in_body"]
    return bonuses["no_tokens_in_body"]


def compute_collision(tokens: list[str], author: str, text: str,
                      link_targets: list[str], query: str,
                      rules: dict) -> float:
    """Score how much the match is a username/token collision.

    Uses substring matching against the full username (catches camelCase and
    concatenated names like ClawClient, walletray, agentmarket).  When every
    body-text token hit also overlaps the username — i.e. no independent
    evidence — the match is treated as a username-dominated collision.
    """
    scores = rules["collision_scores"]

    if not tokens:
        return scores["no_username_overlap"]

    author_tokens = tokenize_username(author)
    author_lower = author.lower()
    text_lower = _normalize(text)
    query_lower = _normalize(query)

    in_uname = lambda t: _token_in_username(t, author_tokens, author_lower, rules)

    username_overlap_count = sum(1 for t in tokens if in_uname(t))
    if username_overlap_count == 0:
        return scores["no_username_overlap"]

    if query_lower in text_lower:
        return scores["no_username_overlap"]
    if any(query_lower in _normalize(lnk) for lnk in link_targets):
        return scores["no_username_overlap"]

    independent_hits = 0
    for t in tokens:
        in_body = t in text_lower
        in_links = any(t in _normalize(lnk) for lnk in link_targets)
        if (in_body or in_links) and not in_uname(t):
            independent_hits += 1

    if independent_hits > 0:
        strict_username_only = 0
        for t in tokens:
            in_body = t in text_lower
            in_links = any(t in _normalize(lnk) for lnk in link_targets)
            if in_uname(t) and not in_body and not in_links:
                strict_username_only += 1
        if strict_username_only == 0:
            return scores["no_username_overlap"]
        ratio = strict_username_only / len(tokens)
    else:
        ratio = username_overlap_count / len(tokens)

    if ratio >= 1.0:
        return scores["all_tokens_username_only"]
    elif ratio >= 0.6:
        return scores["most_tokens_username_only"]
    return scores["some_tokens_username_only"]


def compute_novelty(author: str, text: str, seen_authors: list[str],
                    query_tokens: list[str], link_targets: list[str],
                    rules: dict) -> float:
    """Score author novelty. Seen authors get penalized.

    For seen authors, merely containing query tokens doesn't count as
    "new content" — those tokens are WHY they matched the search in the
    first place. New content means signal markers (API refs, evidence
    language) or non-empty link targets.
    """
    scores = rules["novelty_scores"]
    author_lower = author.lower()
    seen_lower = [a.lower() for a in seen_authors]

    if author_lower not in seen_lower:
        return scores["fresh_author"]

    text_lower = _normalize(text)
    has_new = False

    if link_targets:
        has_new = True

    if not has_new:
        signal_markers = rules.get("signal_boost_patterns", {})
        for markers in signal_markers.values():
            for m in markers:
                if m.lower() in text_lower:
                    has_new = True
                    break
            if has_new:
                break

    if has_new:
        return scores["seen_author_new_content"]
    return scores["seen_author_no_new_content"]


def _build_reason(relevance: float, collision: float, novelty: float,
                  query_tokens: list[str], author: str, text: str,
                  link_targets: list[str], seen_authors: list[str],
                  keep: bool, query: str, rules: dict) -> str:
    parts = []
    author_tokens = tokenize_username(author)
    author_lower = author.lower()
    text_lower = _normalize(text)

    token_overlap = [
        t for t in query_tokens
        if _token_in_username(t, author_tokens, author_lower, rules)
    ]

    if collision >= rules["collision_scores"]["all_tokens_username_only"]:
        parts.append(
            f"collision: query tokens {token_overlap} overlap username '{author}', "
            "no independent body evidence"
        )
    elif collision >= rules["collision_scores"]["most_tokens_username_only"]:
        parts.append(
            f"partial collision: most query tokens {token_overlap} overlap username '{author}'"
        )
    elif collision > 0 and token_overlap:
        parts.append(
            f"collision: query tokens {token_overlap} overlap username '{author}'"
        )

    if relevance >= rules["relevance_bonuses"]["exact_phrase_in_body"]:
        parts.append("exact query phrase found in body text")
    elif relevance >= rules["relevance_bonuses"]["exact_phrase_in_links"]:
        parts.append("exact query phrase found in link targets")
    elif relevance >= rules["relevance_bonuses"]["all_tokens_in_body"]:
        parts.append("all query tokens found in body/links")
    elif relevance <= rules["relevance_bonuses"]["no_tokens_in_body"]:
        parts.append("no query tokens found in body text or links")

    if author_lower in [a.lower() for a in seen_authors]:
        if novelty <= rules["novelty_scores"]["seen_author_no_new_content"]:
            parts.append("seen author with no new relevant content")
        else:
            parts.append("seen author but has some new content")

    if not keep:
        if collision > 0:
            parts.append("discarded as collision")
        elif author_lower in [a.lower() for a in seen_authors] and \
                novelty <= rules["novelty_scores"]["seen_author_no_new_content"]:
            parts.append("discarded as repeated seen author")
        else:
            parts.append("score below keep threshold")

    return "; ".join(parts) if parts else "passed all filters"


def score_result(result: dict, query: str, query_tokens: list[str],
                 seen_authors: list[str], rules: dict) -> dict:
    """Score a single search result."""
    author = result.get("author", "")
    text = result.get("text", "")
    url = result.get("url", "")
    link_targets = result.get("link_targets", [])

    relevance = compute_relevance(query, query_tokens, text, link_targets, rules)
    collision = compute_collision(query_tokens, author, text, link_targets, query, rules)
    novelty = compute_novelty(author, text, seen_authors, query_tokens, link_targets, rules)

    weights = rules["scoring_weights"]
    thresholds = rules["thresholds"]

    combined = (
        weights["relevance"] * relevance
        - weights["collision_penalty"] * collision
        + weights["novelty"] * novelty
    )

    is_hard_collision = collision >= thresholds["collision_discard"]
    is_soft_collision = (
        collision > 0
        and relevance <= rules["relevance_bonuses"]["no_tokens_in_body"]
    )
    is_collision_bait = is_hard_collision or is_soft_collision
    is_stale_seen = (
        author.lower() in [a.lower() for a in seen_authors]
        and novelty <= rules["novelty_scores"]["seen_author_no_new_content"]
    )

    keep = combined >= thresholds["keep_min_combined"] and not is_collision_bait
    if is_stale_seen and relevance < rules["relevance_bonuses"]["all_tokens_in_body"]:
        keep = False

    reason = _build_reason(
        relevance, collision, novelty, query_tokens, author, text,
        link_targets, seen_authors, keep, query, rules
    )

    return {
        "author": author,
        "url": url,
        "relevance_score": round(relevance, 4),
        "collision_score": round(collision, 4),
        "novelty_score": round(novelty, 4),
        "keep": keep,
        "reason": reason,
    }


def reduce_collisions(data: dict, rules: dict | None = None) -> dict:
    """
    Main entry point. Takes search input, returns ranked + filtered results.

    Args:
        data: {"query": str, "results": [...], "seen_authors": [str]}
        rules: optional rules dict (loaded from rules.json if not provided)

    Returns:
        {"ranked_results": [...], "summary": {"discarded_collisions": int, "discarded_seen": int}}
    """
    if rules is None:
        rules = load_rules()

    query = data.get("query", "")
    results = data.get("results", [])
    seen_authors = data.get("seen_authors", [])
    stop_words = rules.get("stop_words", [])

    query_tokens = tokenize_query(query, stop_words)

    scored = []
    for result in results:
        scored.append(
            score_result(result, query, query_tokens, seen_authors, rules)
        )

    scored.sort(
        key=lambda r: (
            r["relevance_score"] - r["collision_score"] + r["novelty_score"]
        ),
        reverse=True,
    )

    no_tokens_threshold = rules["relevance_bonuses"]["no_tokens_in_body"]
    discarded_collisions = sum(
        1 for r in scored
        if not r["keep"] and r["collision_score"] > 0
    )
    discarded_seen = sum(
        1 for r in scored
        if not r["keep"]
        and r["author"].lower() in [a.lower() for a in seen_authors]
        and r["collision_score"] == 0
    )

    return {
        "ranked_results": scored,
        "summary": {
            "discarded_collisions": discarded_collisions,
            "discarded_seen": discarded_seen,
        },
    }


def main():
    """CLI: read JSON from file or stdin, print results."""
    if len(sys.argv) < 2:
        print("Usage: python reducer.py <input.json> [rules.json]", file=sys.stderr)
        print("       cat input.json | python reducer.py -", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    rules_path = sys.argv[2] if len(sys.argv) > 2 else None

    if input_path == "-":
        data = json.load(sys.stdin)
    else:
        with open(input_path, "r") as f:
            data = json.load(f)

    rules = load_rules(rules_path) if rules_path else None
    result = reduce_collisions(data, rules)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
