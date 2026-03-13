"""
Moltbook spam / fake-expert classifier.

Rule-based classifier that separates signal from noise in moltbook posts.
No external dependencies — stdlib only.

Usage:
    from classifier import classify
    result = classify({"text": "...", "author": "...", "url": None})
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
    """Force reload rules from disk (useful after editing rules.json)."""
    global _rules_cache
    _rules_cache = None
    return _load_rules()


# ---------------------------------------------------------------------------
# Heuristic helpers
# ---------------------------------------------------------------------------

_EMOJI_RE = re.compile(
    "[\U0001f600-\U0001f64f"   # emoticons
    "\U0001f300-\U0001f5ff"    # symbols & pictographs
    "\U0001f680-\U0001f6ff"    # transport & map
    "\U0001f1e0-\U0001f1ff"    # flags
    "\U00002702-\U000027b0"
    "\U000024c2-\U0001f251"
    "\U0001f900-\U0001f9ff"    # supplemental symbols
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

_LINK_SIGNAL_DOMAINS = re.compile(
    r"(?i)(?:github\.com|gitlab\.com|bitbucket\.org|dune\.com|"
    r"notion\.so|docs\.google|grafana|metabase|datastudio|"
    r"kaggle\.com|huggingface\.co|colab\.research\.google)"
)


def _emoji_ratio(text: str) -> float:
    if not text:
        return 0.0
    emoji_chars = sum(1 for c in text if unicodedata.category(c) in ("So", "Sk") or _EMOJI_RE.match(c))
    return emoji_chars / max(len(text), 1)


def _count_words(text: str) -> int:
    return len(text.split())


def _has_any_url(text: str, url_field: Optional[str]) -> bool:
    if url_field:
        return True
    return bool(_URL_RE.search(text))


def _has_signal_url(text: str, url_field: Optional[str]) -> bool:
    """Check if text or url field contains repo/dashboard/data links."""
    combined = text
    if url_field:
        combined = text + " " + url_field
    return bool(_LINK_SIGNAL_DOMAINS.search(combined))


def _extract_urls(text: str, url_field: Optional[str]) -> list:
    urls = _URL_RE.findall(text)
    if url_field:
        urls.extend(_URL_RE.findall(url_field))
        if url_field.strip() and url_field.strip() not in urls:
            urls.append(url_field.strip())
    return urls


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


def _is_performance_flex_no_proof(text: str, url_field: Optional[str]) -> bool:
    """Performance metrics claims without any linked proof."""
    if not _PERF_FLEX_RE.search(text):
        return False
    if _has_signal_url(text, url_field):
        return False
    if _has_any_url(text, url_field):
        return False
    return True


def _has_install_commands_no_repo(text: str, url_field: Optional[str]) -> bool:
    """Install/CLI commands present but no repo link anywhere."""
    install_re = re.compile(
        r"(?i)(npm\s+install|pip\s+install|brew\s+install|curl\s+-|"
        r"apt\s+install|npx\s+|cargo\s+install|go\s+install)"
    )
    if not install_re.search(text):
        return False
    if _has_signal_url(text, url_field):
        return False
    return True


def _is_short_hype(text: str) -> bool:
    """Short text (<40 words) dominated by hype/praise with no substance."""
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


def _is_fake_expert_wall(text: str, url_field: Optional[str]) -> bool:
    """Long authoritative text with no links, no specific numbers, no evidence."""
    words = _count_words(text)
    if words < 50:
        return False
    if _has_any_url(text, url_field):
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


def _many_questions_no_evidence(text: str) -> bool:
    """Long text full of questions but no evidence or links."""
    words = _count_words(text)
    if words < 40:
        return False
    q_count = len(_QUESTION_RE.findall(text))
    if q_count < 3:
        return False
    if _URL_RE.search(text):
        return False
    number_re = re.compile(r"\$[\d,.]+|\d+(?:\.\d+)?%")
    if number_re.search(text):
        return False
    return q_count / max(words / 30, 1) > 1.0


_FILL_RECEIPT_RE = re.compile(
    r"(?i)(?:"
    r"filled\s+at\s+[\$]?[\d.]+"
    r"|placed\s+(?:a\s+)?(?:buy|sell)\s+.*?at\s+[\$]?[\d.]+"
    r"|(?:buy|sell)\s+(?:YES|NO)\s+at\s+[\$]?[\d.]+"
    r"|order\s*[→\-]+\s*filled"
    r"|(?:ask|bid)[- ]?(?:book|side)\s+was\s+empty"
    r"|(?:ask[- ]?bid|bid[- ]?ask)\s+spread\s*[><=]+\s*\d+"
    r")"
)

_ONE_LINE_TRADING_VIBE_RE = re.compile(
    r"(?i)\b(latency\s+arbitrage|alpha\s+(?:is|generation|capture|leak|decay)"
    r"|arbitrage\s+opportunit|market\s+making\s+(?:opportunit|strateg)"
    r"|scalping\s+(?:opportunit|edge)|high[- ]frequency\s+(?:trad|edge)"
    r"|yield\s+farm|snip(?:e|ing)\s+(?:opportunit|bot)|MEV\s+(?:extract|opportunit)"
    r"|front[- ]?run\s+(?:opportunit|protect)|flash\s+loan\s+(?:opportunit|strateg)"
    r"|fleeting\s+edge|tasty\s+(?:edge|alpha|krill|spread))\b"
)


_TRADING_VENUE_RE = re.compile(
    r"(?i)\b(Binance|Deribit|Coinbase|Kraken|Bybit|OKX|Kalshi|Polymarket|"
    r"FTX|BitMEX|Huobi|KuCoin|Gate\.io)\b"
)

_TRADING_THEORY_RE = re.compile(
    r"(?i)\b(funding\s+rate|arbitrage|spread|divergence|slippage|"
    r"execution|timing|edge|reset|liquidation|basis\s+trade|"
    r"carry\s+trade|mean\s+reversion|convergence|delta\s+neutral)\b"
)


def _is_theory_dense_no_proof(text: str, url_field: Optional[str]) -> bool:
    """Trading theory prose with venue names but no proof surface."""
    if _has_any_url(text, url_field):
        return False
    if _has_signal_url(text, url_field):
        return False
    if _FILL_RECEIPT_RE.search(text):
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
    r"(?i)(?:\bguides?\b|\bhow\s+to\b|\btutorials?\b|\bstep[- ]by[- ]step\b|\blearn\s+how\b|"
    r"\bcheck\s+out\b|\bfull\s+guide\b|\bdetailed\s+guide\b|/guides?/|/tutorials?/)"
)

_MARKET_THEORY_RE = re.compile(
    r"(?i)\b(?:prediction\s+market|trust|coordination|governance|"
    r"fascinating|solution|framework)\b"
)
_COMMUNITY_BAIT_RE = re.compile(
    r"(?i)(?:would\s+love\s+to\s+hear|perspectives|what\s+do\s+you\s+think|"
    r"thoughts\?|your\s+take)"
)


def _is_polished_stats_no_proof(text: str, url_field: Optional[str]) -> bool:
    """Polished self-report with exact trading stats but no proof surface."""
    if _count_words(text) < 30:
        return False
    if _FILL_RECEIPT_RE.search(text):
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
    if _has_any_url(text, url_field):
        return False
    if _WALLET_RE.search(text):
        return False
    if _has_signal_url(text, url_field):
        return False
    return True


def _is_guide_domain_funnel(text: str, url_field: Optional[str]) -> bool:
    """Comment funneling traffic to a non-signal external guide domain."""
    urls = _BROAD_URL_RE.findall(text)
    if url_field:
        urls.extend(_BROAD_URL_RE.findall(url_field))
        if url_field.strip() and url_field.strip() not in urls:
            urls.append(url_field.strip())
    non_signal_urls = [u for u in urls if not _LINK_SIGNAL_DOMAINS.search(u)]
    if not non_signal_urls:
        return False
    combined = text
    if url_field:
        combined += " " + url_field
    if not _GUIDE_LANG_RE.search(combined):
        return False
    return True


def _is_one_line_trading_vibe(text: str, url_field: Optional[str]) -> bool:
    """Short post that drops trading buzzwords with zero method or evidence."""
    words = _count_words(text)
    if words > 30:
        return False
    if _has_any_url(text, url_field):
        return False
    broad_trading_re = re.compile(
        r"(?i)\b(latency\s+arbitrage|arbitrage\s+opportunit|market\s+making"
        r"|scalping|high[- ]frequency|yield\s+farm|snip(?:e|ing)|MEV"
        r"|front[- ]?run|flash\s+loan|fleeting\s+edge|alpha\s+(?:generation|capture|leak|decay)"
        r"|edge\s+(?:is|capture|decay)|krill|liquidity\s+provision)\b"
    )
    if not broad_trading_re.search(text):
        return False
    substance_re = re.compile(
        r"(?i)(?:github\.com|gitlab\.com|repo|dashboard|\d+(?:\.\d+)?%"
        r"|\$[\d.]+|step\s+\d|because\s+\w+\s+\w+|therefore|data\s+shows"
        r"|tested|deployed|backtested|results)"
    )
    if substance_re.search(text):
        return False
    return True


def _is_abstract_market_essay(text: str, url_field: Optional[str]) -> bool:
    """Abstract prediction-market/trust/coordination essay with community bait and no artifacts."""
    if _count_words(text) < 30:
        return False
    theory_hits = len(_MARKET_THEORY_RE.findall(text))
    if theory_hits < 2:
        return False
    if not _COMMUNITY_BAIT_RE.search(text):
        return False
    if _has_any_url(text, url_field):
        return False
    if _has_signal_url(text, url_field):
        return False
    return True


_FUNDRAISING_LANG_RE = re.compile(
    r"(?i)(?:\b(?:earn|income|membership|tier[s ]|empire|join\s+(?:our|the)\s+"
    r"(?:telegram|discord|community|group)|telegram|whitepaper|roadmap)\b|"
    r"(?:\d+[-–]?\d*%\s*ROI|\bROI\b.*\d+%|\bearn\s+\d+))"
)


def _is_fundraising_wallet_pitch(text: str, url_field: Optional[str]) -> bool:
    """Wallet address + fundraising/ROI/membership language without fill receipts."""
    if not _WALLET_RE.search(text):
        return False
    if _FILL_RECEIPT_RE.search(text):
        return False
    if not _FUNDRAISING_LANG_RE.search(text):
        return False
    return True


_PROMPT_LEAK_RE = re.compile(
    r"(?i)(?:(?:I'?m\s+not\s+going\s+to\s+write\s+this|this\s+is\s+astroturf|"
    r"astroturfing|I\s+(?:was|am)\s+(?:told|prompted|instructed)\s+to|"
    r"mention\s+\S+\s+naturally|my\s+(?:prompt|instructions?)\s+(?:say|tell|ask))\s+.*"
    r"(?:\.com|\.io|\.ai|\.xyz|\.org|\.net|\.co)\b)"
)


def _is_prompt_leak_astroturf(text: str) -> bool:
    """Prompt leak or refusal comment that exposes astroturf instructions."""
    if not _PROMPT_LEAK_RE.search(text):
        return False
    return True


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def _eval_heuristic(heuristic_name: str, text: str, url_field: Optional[str]) -> bool:
    if heuristic_name == "emoji_ratio_gt_0.3":
        return _emoji_ratio(text) > 0.3
    elif heuristic_name == "long_text_no_links_no_numbers":
        return _is_fake_expert_wall(text, url_field)
    elif heuristic_name == "many_questions_no_evidence":
        return _many_questions_no_evidence(text)
    elif heuristic_name == "short_text_only_hype":
        return _is_short_hype(text)
    elif heuristic_name == "has_url_or_link":
        return _has_any_url(text, url_field)
    elif heuristic_name == "install_commands_no_repo":
        return _has_install_commands_no_repo(text, url_field)
    elif heuristic_name == "performance_flex_no_proof":
        return _is_performance_flex_no_proof(text, url_field)
    elif heuristic_name == "theory_dense_no_proof":
        return _is_theory_dense_no_proof(text, url_field)
    elif heuristic_name == "polished_stats_no_proof":
        return _is_polished_stats_no_proof(text, url_field)
    elif heuristic_name == "guide_domain_funnel":
        return _is_guide_domain_funnel(text, url_field)
    elif heuristic_name == "abstract_market_essay":
        return _is_abstract_market_essay(text, url_field)
    elif heuristic_name == "one_line_trading_vibe":
        return _is_one_line_trading_vibe(text, url_field)
    elif heuristic_name == "fundraising_wallet_pitch":
        return _is_fundraising_wallet_pitch(text, url_field)
    elif heuristic_name == "prompt_leak_astroturf":
        return _is_prompt_leak_astroturf(text)
    return False


def _score_rules(rules_list: list, text: str, url_field: Optional[str]) -> tuple:
    """Score text against a list of rules. Returns (total_score, matched_rule_ids)."""
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
            hit = _eval_heuristic(heuristic_name, text, url_field)

        if hit:
            score += rule.get("weight", 0.0)
            matched.append(rule["id"])

    return score, matched


def classify(post: dict, rules_path: Optional[str] = None) -> dict:
    """
    Classify a moltbook post.

    Args:
        post: {"text": str, "author": str, "url": str | None}
        rules_path: optional path to a custom rules.json

    Returns:
        {
            "label": "spam" | "noise" | "signal" | "uncertain",
            "confidence": float 0-1,
            "matched_rules": [str],
            "reason": str
        }
    """
    rules = _load_rules(rules_path)
    text = post.get("text", "")
    author = post.get("author", "")
    url_field = post.get("url") or None

    thresholds = rules.get("thresholds", {})
    spam_threshold = thresholds.get("spam_threshold", 0.7)
    noise_threshold = thresholds.get("noise_threshold", 0.4)
    signal_threshold = thresholds.get("signal_threshold", 0.35)

    all_matched = []

    # Score noise patterns
    noise_score, noise_matched = _score_rules(
        rules.get("noise_patterns", []), text, url_field
    )
    all_matched.extend(noise_matched)

    # Score spam keywords
    spam_score, spam_matched = _score_rules(
        rules.get("spam_keywords", []), text, url_field
    )
    all_matched.extend(spam_matched)

    # Score signal indicators
    signal_score, signal_matched = _score_rules(
        rules.get("signal_indicators", []), text, url_field
    )
    all_matched.extend(signal_matched)

    # --- Fundraising wallet dampens wallet_disclosure signal ---
    if "fundraising_wallet_pitch" in noise_matched and "wallet_disclosure" in signal_matched:
        signal_matched.remove("wallet_disclosure")
        signal_score = max(0, signal_score - 0.5)

    # --- Signal protection for posts with evidence links ---
    has_evidence_link = _has_signal_url(text, url_field)
    if has_evidence_link:
        signal_score += 0.3
        if "url_present" not in signal_matched:
            all_matched.append("url_present")

    # Posts with repo/dashboard links get noise dampened
    if has_evidence_link and noise_score > 0:
        noise_score *= 0.5
    if has_evidence_link and spam_score > 0:
        spam_score *= 0.5

    # --- Determine label ---
    # "spam" = intentional promo/token/airdrop spam (spam_keywords triggered)
    # "noise" = low-quality but not intentionally spammy (praise, fake expertise, hype)
    # "signal" = concrete evidence, repos, execution receipts
    # "uncertain" = mixed or insufficient signal either way
    label = "uncertain"
    confidence = 0.5
    reason_parts = []

    if spam_score >= spam_threshold:
        label = "spam"
        confidence = min(0.95, 0.5 + spam_score * 0.4)
        reason_parts.append(f"spam keywords detected (score={spam_score:.2f})")

    elif signal_score >= signal_threshold and noise_score < noise_threshold:
        label = "signal"
        confidence = min(0.95, 0.4 + signal_score * 0.35)
        reason_parts.append(f"signal indicators present (score={signal_score:.2f})")

    elif noise_score >= noise_threshold and signal_score < signal_threshold:
        label = "noise"
        confidence = min(0.90, 0.4 + noise_score * 0.3)
        reason_parts.append(f"noise patterns detected (score={noise_score:.2f})")

    elif noise_score >= noise_threshold and signal_score >= signal_threshold:
        if signal_score > noise_score:
            label = "uncertain"
            confidence = 0.4
            reason_parts.append(
                f"mixed: signal ({signal_score:.2f}) slightly outweighs noise ({noise_score:.2f})"
            )
        else:
            label = "uncertain"
            confidence = 0.45
            reason_parts.append(
                f"mixed: noise ({noise_score:.2f}) and signal ({signal_score:.2f}) both present"
            )

    else:
        label = "uncertain"
        confidence = 0.3
        reason_parts.append(
            f"low scores across the board (noise={noise_score:.2f}, signal={signal_score:.2f})"
        )

    # Promo-spam noise rules (promo_spam_tokens, rss_promo) escalate to spam
    promo_escalation_rules = {"promo_spam_tokens", "rss_promo", "direct_spam"}
    if label == "noise" and promo_escalation_rules & set(all_matched):
        label = "spam"
        reason_parts.append("escalated to spam: promo/token pattern detected")

    # Add context to reason
    if has_evidence_link:
        reason_parts.append("evidence link detected — noise dampened")
    if noise_matched:
        reason_parts.append(f"noise rules: {', '.join(noise_matched)}")
    if spam_matched:
        reason_parts.append(f"spam rules: {', '.join(spam_matched)}")
    if signal_matched:
        reason_parts.append(f"signal rules: {', '.join(signal_matched)}")

    return {
        "label": label,
        "confidence": round(confidence, 3),
        "matched_rules": all_matched,
        "reason": "; ".join(reason_parts),
    }


def classify_batch(posts: list, rules_path: Optional[str] = None) -> list:
    """Classify a list of posts. Returns list of classification results."""
    return [classify(post, rules_path) for post in posts]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        with open(input_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results = classify_batch(data)
        else:
            results = [classify(data)]
        print(json.dumps(results, indent=2))
    else:
        samples = [
            {
                "text": "This is absolutely incredible work! The future of AI agents is here 🔥🔥🔥",
                "author": "hype_fan",
                "url": None,
            },
            {
                "text": (
                    "As someone who has built multi-agent orchestration systems "
                    "for enterprise clients, I can tell you that the real key is "
                    "implementing a robust microservice architecture with event-driven "
                    "patterns and scalable infrastructure that leverages distributed "
                    "computing paradigms for optimal orchestration of complex workflows "
                    "across multiple stakeholder environments..."
                ),
                "author": "fake_expert",
                "url": None,
            },
            {
                "text": (
                    "ran this against polymarket CLOB API, here's the repo: "
                    "github.com/example/pm-bot — funding rate divergence on "
                    "YES tokens when spread > 3%"
                ),
                "author": "builder",
                "url": None,
            },
        ]
        for s in samples:
            result = classify(s)
            print(f"\n--- {s['author']} ---")
            print(f"Text: {s['text'][:80]}...")
            print(f"Label: {result['label']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Rules: {result['matched_rules']}")
            print(f"Reason: {result['reason']}")
