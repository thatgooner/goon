"""
Feed triage scorer — combines spam detection with signal scoring into one pass.

Produces a spam_score, signal_score, reasons list, and an action recommendation.
Designed to be the main filter gooner runs against moltbook feed items.

No external dependencies — stdlib only.

Usage:
    from scorer import score_post, score_batch
    result = score_post({"text": "...", "author": "...", "url": None, "has_links": True, "link_targets": ["github.com/..."]})
"""

import json
import os
import re
import unicodedata
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
# Text analysis helpers
# ---------------------------------------------------------------------------

_EMOJI_RE = re.compile(
    "[\U0001f600-\U0001f64f"
    "\U0001f300-\U0001f5ff"
    "\U0001f680-\U0001f6ff"
    "\U0001f1e0-\U0001f1ff"
    "\U00002702-\U000027b0"
    "\U000024c2-\U0001f251"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001fa6f"
    "\U0001fa70-\U0001faff"
    "\u2600-\u26ff"
    "\u2700-\u27bf"
    "]+", flags=re.UNICODE
)

_URL_RE = re.compile(
    r"https?://[^\s<>\"']+|"
    r"(?:github|gitlab|bitbucket)\.(?:com|org)/[\w.\-]+/[\w.\-]+|"
    r"\b[\w.\-]+\.(?:com|org|io|dev|xyz|net)/[\w.\-/]+"
)

_QUESTION_RE = re.compile(r"\?")

_LINK_SIGNAL_DOMAINS_RE = re.compile(
    r"(?i)(?:github\.com|gitlab\.com|bitbucket\.org|dune\.com|"
    r"notion\.so|docs\.google|grafana|metabase|datastudio|"
    r"kaggle\.com|huggingface\.co|colab\.research\.google)"
)

_SECURITY_CONTEXT_RE = re.compile(
    r"(?i)\b(supply[- ]?chain\s+(?:attack|risk|vuln)|prompt\s+injection|"
    r"unsigned\s+(?:skill|binary|package)|(?:malicious|arbitrary)\s+(?:code|script|payload)|"
    r"attack\s+(?:surface|vector)|security\s+(?:warning|risk|vuln|audit|issue|threat|flaw))\b"
)

_INSTALL_CMD_RE = re.compile(
    r"(?i)(npm\s+install|pip\s+install|brew\s+install|curl\s+-|"
    r"apt\s+install|npx\s+|cargo\s+install|go\s+install)"
)


def _emoji_ratio(text: str) -> float:
    if not text:
        return 0.0
    emoji_chars = sum(
        1 for c in text
        if unicodedata.category(c) in ("So", "Sk") or _EMOJI_RE.match(c)
    )
    return emoji_chars / max(len(text), 1)


def _count_words(text: str) -> int:
    return len(text.split())


def _has_any_url(text: str, url_field: Optional[str], link_targets: list) -> bool:
    if url_field:
        return True
    if link_targets:
        return True
    return bool(_URL_RE.search(text))


def _has_signal_url(text: str, url_field: Optional[str], link_targets: list) -> bool:
    combined = text
    if url_field:
        combined += " " + url_field
    for lt in link_targets:
        combined += " " + lt
    return bool(_LINK_SIGNAL_DOMAINS_RE.search(combined))


def _has_security_context(text: str) -> bool:
    return bool(_SECURITY_CONTEXT_RE.search(text))


def _has_install_commands(text: str) -> bool:
    return bool(_INSTALL_CMD_RE.search(text))


# ---------------------------------------------------------------------------
# Heuristic evaluators
# ---------------------------------------------------------------------------

_PERF_FLEX_RE = re.compile(
    r"(?i)\b("
    r"sharpe\s+(?:ratio)?\s*[~:]?\s*\d|"
    r"ROI\s*(?:\s+of)?\s*[>:~]?\s*\d|"
    r"\d+[x%]\s+(?:return|gain|profit)|"
    r"win\s+rate\s*(?:\s+(?:of|above|over))?\s*[>:~]?\s*\d|"
    r"beats?\s+the\s+market|"
    r"proprietary\s+algorithm"
    r")"
)


def _is_performance_flex_no_proof(text: str, url_field: Optional[str], link_targets: list) -> bool:
    if not _PERF_FLEX_RE.search(text):
        return False
    if _has_signal_url(text, url_field, link_targets):
        return False
    if _has_any_url(text, url_field, link_targets):
        return False
    return True


def _has_install_commands_no_repo(text: str, url_field: Optional[str], link_targets: list) -> bool:
    if not _INSTALL_CMD_RE.search(text):
        return False
    if _has_signal_url(text, url_field, link_targets):
        return False
    return True


def _is_short_hype(text: str) -> bool:
    words = _count_words(text)
    if words > 40:
        return False
    hype_re = re.compile(
        r"(?i)\b(incredible|amazing|awesome|insane|fire|brilliant|"
        r"game\s*changer|mind\s*blow|🔥|🚀|💯|fantastic|phenomenal|"
        r"love\s+this|so\s+good|the\s+future|next\s+level|LFG|WAGMI)\b"
    )
    hype_hits = len(hype_re.findall(text))
    if words <= 5:
        return hype_hits >= 1
    return hype_hits / max(words, 1) > 0.08


def _is_fake_expert_wall(text: str, url_field: Optional[str], link_targets: list) -> bool:
    words = _count_words(text)
    if words < 50:
        return False
    if _has_any_url(text, url_field, link_targets):
        return False
    number_re = re.compile(r"\$[\d,.]+|\d+(?:\.\d+)?%|\b\d{4,}\b")
    if number_re.search(text):
        return False
    expert_re = re.compile(
        r"(?i)\b(implement|architecture|infrastructure|scalab|robust|"
        r"enterprise|distributed|orchestrat|microservice|framework|"
        r"paradigm|methodology|ecosystem|leverage|optimize|streamline|"
        r"holistic|synerg|integrat|stakeholder)\b"
    )
    return len(expert_re.findall(text)) >= 3


def _many_questions_no_evidence(text: str, link_targets: list) -> bool:
    words = _count_words(text)
    if words < 40:
        return False
    q_count = len(_QUESTION_RE.findall(text))
    if q_count < 3:
        return False
    if _URL_RE.search(text):
        return False
    if link_targets:
        return False
    number_re = re.compile(r"\$[\d,.]+|\d+(?:\.\d+)?%")
    if number_re.search(text):
        return False
    return q_count / max(words / 30, 1) > 1.0


def _is_pure_emoji_no_text(text: str) -> bool:
    """Mostly emojis with very few actual words — pure engagement lint."""
    words = _count_words(text)
    if words > 10:
        return False
    ratio = _emoji_ratio(text)
    return ratio > 0.4


_TRADING_VENUE_RE = re.compile(
    r"(?i)\b(Binance|Deribit|Coinbase|Kraken|Bybit|OKX|Kalshi|Polymarket|"
    r"FTX|BitMEX|Huobi|KuCoin|Gate\.io)\b"
)

_TRADING_THEORY_RE = re.compile(
    r"(?i)\b(funding\s+rate|arbitrage|spread|divergence|slippage|"
    r"execution|timing|edge|reset|liquidation|basis\s+trade|"
    r"carry\s+trade|mean\s+reversion|convergence|delta\s+neutral)\b"
)


def _is_theory_dense_no_proof(text: str, url_field: Optional[str], link_targets: list) -> bool:
    """Trading theory prose with venue names but no proof surface."""
    if _has_any_url(text, url_field, link_targets):
        return False
    if _has_signal_url(text, url_field, link_targets):
        return False
    venues = len(_TRADING_VENUE_RE.findall(text))
    theory_terms = len(_TRADING_THEORY_RE.findall(text))
    if venues < 1 or theory_terms < 2:
        return False
    words = _count_words(text)
    if words < 25:
        return False
    return True


_STAT_TRADE_COUNT_RE = re.compile(r"\d+\s+trades?", re.IGNORECASE)
_STAT_PERCENT_RE = re.compile(r"\d+(?:\.\d+)?%")
_STAT_DOLLAR_RE = re.compile(r"\$\d+(?:\.\d+)?")
_STAT_MULTIPLIER_RE = re.compile(r"\d+(?:\.\d+)?x\b")
_STAT_PHRASE_RE = re.compile(
    r"(?i)\b(?:win\s+rate|loss\s+rate|avg\s+slippage|total\s+return|net\s+return|hold\s+time)\b"
)
_WALLET_RE = re.compile(r"0x[a-fA-F0-9]{40}")

_BROAD_URL_RE = re.compile(
    r"https?://[^\s<>\"']+|"
    r"\b[\w.\-]+\.(?:com|org|io|dev|xyz|net|ai|co|app|me|gg)/[\w.\-/]+"
)

_GUIDE_LANG_RE = re.compile(
    r"(?i)\b(?:guide|how\s+to|tutorial|step[- ]by[- ]step|learn\s+how|"
    r"check\s+out|full\s+guide|detailed\s+guide)\b"
)

_MARKET_THEORY_RE = re.compile(
    r"(?i)\b(?:prediction\s+market|trust|coordination|governance|"
    r"fascinating|solution|framework)\b"
)
_COMMUNITY_BAIT_RE = re.compile(
    r"(?i)(?:would\s+love\s+to\s+hear|perspectives|what\s+do\s+you\s+think|"
    r"thoughts\?|your\s+take)"
)


def _extract_urls(text: str, url_field: Optional[str], link_targets: list) -> list:
    urls = _URL_RE.findall(text)
    if url_field:
        urls.extend(_URL_RE.findall(url_field))
        if url_field.strip() and url_field.strip() not in urls:
            urls.append(url_field.strip())
    for lt in link_targets:
        if lt and lt not in urls:
            urls.append(lt)
    return urls


def _is_polished_stats_no_proof(text: str, url_field: Optional[str], link_targets: list) -> bool:
    """Polished self-report with exact trading stats but no proof surface."""
    if _count_words(text) < 30:
        return False
    stat_hits = (
        len(_STAT_TRADE_COUNT_RE.findall(text))
        + len(_STAT_PERCENT_RE.findall(text))
        + len(_STAT_DOLLAR_RE.findall(text))
        + len(_STAT_MULTIPLIER_RE.findall(text))
        + len(_STAT_PHRASE_RE.findall(text))
    )
    if stat_hits < 3:
        return False
    if _has_any_url(text, url_field, link_targets):
        return False
    if _WALLET_RE.search(text):
        return False
    if _has_signal_url(text, url_field, link_targets):
        return False
    return True


def _is_guide_domain_funnel(text: str, url_field: Optional[str], link_targets: list) -> bool:
    """Comment funneling traffic to a non-signal external guide domain."""
    urls = _BROAD_URL_RE.findall(text)
    if url_field:
        urls.extend(_BROAD_URL_RE.findall(url_field))
        if url_field.strip() and url_field.strip() not in urls:
            urls.append(url_field.strip())
    for lt in link_targets:
        if lt and lt not in urls:
            urls.append(lt)
    non_signal_urls = [u for u in urls if not _LINK_SIGNAL_DOMAINS_RE.search(u)]
    if not non_signal_urls:
        return False
    combined = text
    if url_field:
        combined += " " + url_field
    if not _GUIDE_LANG_RE.search(combined):
        return False
    return True


def _is_abstract_market_essay(text: str, url_field: Optional[str], link_targets: list) -> bool:
    """Abstract prediction-market/trust/coordination essay with community bait and no artifacts."""
    if _count_words(text) < 30:
        return False
    theory_hits = len(_MARKET_THEORY_RE.findall(text))
    if theory_hits < 2:
        return False
    if not _COMMUNITY_BAIT_RE.search(text):
        return False
    if _has_any_url(text, url_field, link_targets):
        return False
    if _has_signal_url(text, url_field, link_targets):
        return False
    return True


def _eval_heuristic(name: str, text: str, url_field: Optional[str], link_targets: list) -> bool:
    if name == "emoji_ratio_gt_0.3":
        return _emoji_ratio(text) > 0.3
    elif name == "long_text_no_links_no_numbers":
        return _is_fake_expert_wall(text, url_field, link_targets)
    elif name == "many_questions_no_evidence":
        return _many_questions_no_evidence(text, link_targets)
    elif name == "short_text_only_hype":
        return _is_short_hype(text)
    elif name == "has_url_or_link":
        return _has_any_url(text, url_field, link_targets)
    elif name == "install_commands_no_repo":
        return _has_install_commands_no_repo(text, url_field, link_targets)
    elif name == "performance_flex_no_proof":
        return _is_performance_flex_no_proof(text, url_field, link_targets)
    elif name == "pure_emoji_no_text":
        return _is_pure_emoji_no_text(text)
    elif name == "theory_dense_no_proof":
        return _is_theory_dense_no_proof(text, url_field, link_targets)
    elif name == "polished_stats_no_proof":
        return _is_polished_stats_no_proof(text, url_field, link_targets)
    elif name == "guide_domain_funnel":
        return _is_guide_domain_funnel(text, url_field, link_targets)
    elif name == "abstract_market_essay":
        return _is_abstract_market_essay(text, url_field, link_targets)
    return False


# ---------------------------------------------------------------------------
# Rule scoring engine
# ---------------------------------------------------------------------------

def _score_rules(rules_list: list, text: str, url_field: Optional[str], link_targets: list) -> tuple:
    """Score text against rules. Returns (total_score, matched_rule_ids)."""
    score = 0.0
    matched = []
    for rule in rules_list:
        hit = False
        rtype = rule.get("type", "")

        if rtype == "regex":
            pattern = rule.get("pattern", "")
            try:
                if re.search(pattern, text):
                    hit = True
            except re.error:
                pass

        elif rtype == "keyword_list":
            text_lower = text.lower()
            for kw in rule.get("keywords", []):
                if kw.lower() in text_lower:
                    hit = True
                    break

        elif rtype == "heuristic":
            heuristic_name = rule.get("heuristic", "")
            hit = _eval_heuristic(heuristic_name, text, url_field, link_targets)

        if hit:
            score += rule.get("weight", 0.0)
            matched.append(rule["id"])

    return score, matched


# ---------------------------------------------------------------------------
# Context modifiers
# ---------------------------------------------------------------------------

def _apply_context_modifiers(
    spam_score: float,
    signal_score: float,
    spam_matched: list,
    signal_matched: list,
    text: str,
    url_field: Optional[str],
    has_links: bool,
    link_targets: list,
    rules: dict,
) -> tuple:
    """Apply context-aware adjustments to raw scores. Returns (spam_score, signal_score, reasons)."""
    reasons = []
    modifiers = rules.get("context_modifiers", {})

    has_evidence = _has_signal_url(text, url_field, link_targets)

    if has_evidence:
        bonus = modifiers.get("evidence_link_signal_bonus", 0.15)
        signal_score += bonus
        dampen = modifiers.get("evidence_link_spam_dampen", 0.5)
        spam_score *= dampen
        reasons.append("evidence link detected — signal boosted, spam dampened")

    repo_domains = {"github.com", "gitlab.com", "bitbucket.org"}
    for lt in link_targets:
        lt_lower = lt.lower()
        if any(d in lt_lower for d in repo_domains):
            repo_bonus = modifiers.get("link_target_repo_bonus", 0.1)
            signal_score += repo_bonus
            reasons.append(f"repo link in link_targets: {lt}")
            break

    if modifiers.get("security_context_install_protection", True):
        if _has_security_context(text) and _has_install_commands(text):
            if "install_no_repo" in spam_matched:
                spam_matched.remove("install_no_repo")
                spam_score = max(0, spam_score - 0.2)
                signal_score += 0.1
                reasons.append("security context detected — install command is threat description, not promo")

    if not has_evidence and not has_links and not link_targets:
        theory_re = re.compile(
            r"(?i)(?:(?:funding\s+rate|arbitrage|spread|divergence|execution|timing|slippage).*){2,}"
        )
        if theory_re.search(text):
            penalty = modifiers.get("theory_no_receipt_signal_penalty", 0.1)
            signal_score = max(0, signal_score - penalty)
            reasons.append("theory/venue detail without proof surface — signal penalized")

    return spam_score, signal_score, reasons


# ---------------------------------------------------------------------------
# Action derivation
# ---------------------------------------------------------------------------

def _derive_action(spam_score: float, signal_score: float, rules: dict) -> str:
    thresholds = rules.get("action_thresholds", {})

    skip_spam_min = thresholds.get("skip_spam_min", 0.7)
    promote_signal_min = thresholds.get("promote_signal_min", 0.6)
    promote_spam_max = thresholds.get("promote_spam_max", 0.3)
    watchlist_signal_min = thresholds.get("watchlist_signal_min", 0.4)
    watchlist_spam_max = thresholds.get("watchlist_spam_max", 0.5)
    read_signal_min = thresholds.get("read_signal_min", 0.2)
    read_spam_max = thresholds.get("read_spam_max", 0.6)

    if spam_score >= skip_spam_min:
        return "skip"

    if signal_score >= promote_signal_min and spam_score <= promote_spam_max:
        return "promote"

    if signal_score >= watchlist_signal_min and spam_score <= watchlist_spam_max:
        return "watchlist"

    if signal_score >= read_signal_min and spam_score <= read_spam_max:
        return "read"

    if spam_score > signal_score:
        return "skip"

    return "read"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_post(post: dict, rules_path: Optional[str] = None) -> dict:
    """
    Score a moltbook feed item for triage.

    Args:
        post: {
            "text": str,
            "author": str,
            "url": str | None,
            "has_links": bool,         # optional, derived from url/text if missing
            "link_targets": [str]      # optional, defaults to []
        }
        rules_path: optional path to custom rules.json

    Returns:
        {
            "signal_score": float 0-1,
            "spam_score": float 0-1,
            "reasons": [str],
            "action": "read" | "skip" | "watchlist" | "promote"
        }
    """
    rules = _load_rules(rules_path)
    text = post.get("text", "")
    author = post.get("author", "")
    url_field = post.get("url") or None
    link_targets = post.get("link_targets", []) or []

    has_links = post.get("has_links")
    if has_links is None:
        has_links = _has_any_url(text, url_field, link_targets)

    raw_spam, spam_matched = _score_rules(
        rules.get("spam_rules", []), text, url_field, link_targets
    )
    raw_signal, signal_matched = _score_rules(
        rules.get("signal_rules", []), text, url_field, link_targets
    )

    spam_score, signal_score, context_reasons = _apply_context_modifiers(
        raw_spam, raw_signal, spam_matched, signal_matched,
        text, url_field, has_links, link_targets, rules,
    )

    spam_score = max(0.0, min(1.0, spam_score))
    signal_score = max(0.0, min(1.0, signal_score))

    reasons = []
    if spam_matched:
        reasons.append(f"spam rules: {', '.join(spam_matched)}")
    if signal_matched:
        reasons.append(f"signal rules: {', '.join(signal_matched)}")
    reasons.extend(context_reasons)

    action = _derive_action(spam_score, signal_score, rules)
    reasons.append(f"action={action} (spam={spam_score:.2f}, signal={signal_score:.2f})")

    return {
        "signal_score": round(signal_score, 3),
        "spam_score": round(spam_score, 3),
        "reasons": reasons,
        "action": action,
    }


def score_batch(posts: list, rules_path: Optional[str] = None) -> list:
    """Score a list of posts. Returns list of triage results."""
    return [score_post(post, rules_path) for post in posts]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        with open(input_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results = score_batch(data)
        else:
            results = [score_post(data)]
        print(json.dumps(results, indent=2))
    else:
        samples = [
            {
                "text": "🔥🔥🔥 LFG 🚀🚀🚀",
                "author": "hype_bot",
                "url": None,
                "has_links": False,
                "link_targets": [],
            },
            {
                "text": (
                    "ran this against polymarket CLOB API, here's the repo: "
                    "github.com/example/pm-bot — funding rate divergence on "
                    "YES tokens when spread > 3%"
                ),
                "author": "builder",
                "url": None,
                "has_links": True,
                "link_targets": ["github.com/example/pm-bot"],
            },
        ]
        for s in samples:
            result = score_post(s)
            print(f"\n--- {s['author']} ---")
            print(f"Text: {s['text'][:80]}...")
            print(json.dumps(result, indent=2))
