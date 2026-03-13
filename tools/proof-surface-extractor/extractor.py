"""
Proof-surface extractor for moltbook posts.

Detects auditable proof surfaces (repos, dashboards, wallets, fill receipts,
docs, sites, polymarket profiles) and produces a verdict: no_proof,
partial_proof, or linked_proof.

No external dependencies — stdlib only.

Usage:
    from extractor import extract
    result = extract({
        "text": "...",
        "author": "...",
        "url": None,
        "link_targets": ["https://github.com/example/repo"],
        "notes": None
    })
"""

import json
import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

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
# URL extraction
# ---------------------------------------------------------------------------

_URL_RE = re.compile(
    r"https?://[^\s<>\"\')}\]]+", re.IGNORECASE
)


def _extract_urls(text: str) -> list[str]:
    urls = _URL_RE.findall(text)
    cleaned = []
    for u in urls:
        u = u.rstrip(".,;:!?)")
        if u not in cleaned:
            cleaned.append(u)
    return cleaned


def _parse_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        return host.lower().lstrip("www.")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Surface detectors
# ---------------------------------------------------------------------------

def _detect_repos(urls: list[str], rules: dict) -> list[dict]:
    surfaces = []
    seen = set()
    repo_domains = rules.get("repo_domains", [])
    for url in urls:
        domain = _parse_domain(url)
        for rd in repo_domains:
            if domain == rd or domain.endswith("." + rd):
                parsed = urlparse(url)
                path = parsed.path.strip("/")
                parts = path.split("/")
                if len(parts) >= 2:
                    repo_path = "/".join(parts[:2])
                    key = f"{domain}/{repo_path}"
                    if key not in seen:
                        seen.add(key)
                        surfaces.append({
                            "type": "repo",
                            "value": url,
                            "confidence": 0.9
                        })
                break
    return surfaces


def _detect_dashboards(urls: list[str], rules: dict) -> list[dict]:
    surfaces = []
    seen = set()
    dashboard_domains = rules.get("dashboard_domains", [])
    for url in urls:
        domain = _parse_domain(url)
        for dd in dashboard_domains:
            if domain == dd or domain.endswith("." + dd) or dd in domain:
                if url not in seen:
                    seen.add(url)
                    surfaces.append({
                        "type": "dashboard",
                        "value": url,
                        "confidence": 0.85
                    })
                break
    return surfaces


def _detect_docs(urls: list[str], rules: dict) -> list[dict]:
    surfaces = []
    seen = set()
    docs_domains = rules.get("docs_domains", [])
    docs_paths = rules.get("docs_path_patterns", [])
    for url in urls:
        domain = _parse_domain(url)
        parsed = urlparse(url)
        path = parsed.path.lower()

        is_docs = False
        for dd in docs_domains:
            if domain == dd or domain.endswith("." + dd) or dd in domain:
                is_docs = True
                break

        if not is_docs:
            for dp in docs_paths:
                if dp in path:
                    is_docs = True
                    break

        if is_docs and url not in seen:
            seen.add(url)
            surfaces.append({
                "type": "docs",
                "value": url,
                "confidence": 0.8
            })
    return surfaces


def _detect_polymarket_profiles(urls: list[str], rules: dict) -> list[dict]:
    surfaces = []
    pm_domains = rules.get("polymarket_domains", [])
    for url in urls:
        domain = _parse_domain(url)
        for pd in pm_domains:
            if domain == pd or domain.endswith("." + pd):
                parsed = urlparse(url)
                path = parsed.path.strip("/")
                if path.startswith("profile") or path.startswith("portfolio"):
                    surfaces.append({
                        "type": "polymarket_profile",
                        "value": url,
                        "confidence": 0.85
                    })
                break
    return surfaces


def _detect_wallets(text: str, rules: dict) -> list[dict]:
    surfaces = []
    seen = set()
    wallet_patterns = rules.get("wallet_patterns", {})

    eth_re = re.compile(wallet_patterns.get("ethereum", ""), re.IGNORECASE)
    for m in eth_re.finditer(text):
        val = m.group(0)
        if val not in seen and not _is_inside_url(text, m.start(), m.end()):
            seen.add(val)
            surfaces.append({
                "type": "wallet",
                "value": val,
                "confidence": 0.85
            })

    return surfaces


def _is_inside_url(text: str, start: int, end: int) -> bool:
    """Check if a match span is embedded inside a URL."""
    line_start = text.rfind("\n", 0, start) + 1
    prefix = text[line_start:start]
    if "http://" in prefix or "https://" in prefix:
        space_pos = prefix.rfind(" ")
        url_start = prefix.rfind("http", space_pos if space_pos >= 0 else 0)
        if url_start >= 0:
            return True
    return False


def _detect_fill_receipts(text: str, rules: dict) -> list[dict]:
    surfaces = []
    text_lower = text.lower()

    phrase_hits = []
    for phrase in rules.get("fill_receipt_phrases", []):
        if phrase.lower() in text_lower:
            phrase_hits.append(phrase)

    pattern_hits = []
    for pat in rules.get("fill_receipt_patterns", []):
        if re.search(pat, text, re.IGNORECASE):
            pattern_hits.append(pat)

    if phrase_hits or pattern_hits:
        confidence = min(0.95, 0.4 + 0.15 * len(phrase_hits) + 0.2 * len(pattern_hits))
        detail_parts = []
        if phrase_hits:
            detail_parts.append("phrases: " + ", ".join(phrase_hits[:3]))
        if pattern_hits:
            detail_parts.append(f"{len(pattern_hits)} pattern match(es)")
        surfaces.append({
            "type": "fill_receipt",
            "value": "; ".join(detail_parts),
            "confidence": round(confidence, 2)
        })

    return surfaces


def _detect_sites(urls: list[str], rules: dict, other_surfaces: list[dict]) -> list[dict]:
    """Detect generic site URLs that aren't already classified as repo/dashboard/docs/polymarket."""
    surfaces = []
    already_classified = {s["value"] for s in other_surfaces}

    repo_domains = set(rules.get("repo_domains", []))
    dashboard_domains = set(rules.get("dashboard_domains", []))
    docs_domains = set(rules.get("docs_domains", []))
    pm_domains = set(rules.get("polymarket_domains", []))
    skip_domains = repo_domains | dashboard_domains | docs_domains | pm_domains

    moltbook_domains = {"moltbook.com", "twitter.com", "x.com", "t.co"}

    for url in urls:
        if url in already_classified:
            continue
        domain = _parse_domain(url)
        if not domain:
            continue

        is_skip = False
        for sd in skip_domains:
            if domain == sd or domain.endswith("." + sd) or sd in domain:
                is_skip = True
                break
        if is_skip:
            continue

        if domain in moltbook_domains:
            continue

        surfaces.append({
            "type": "site",
            "value": url,
            "confidence": 0.6
        })

    return surfaces


# ---------------------------------------------------------------------------
# Missing-expected detection
# ---------------------------------------------------------------------------

def _detect_missing_expected(text: str, surfaces: list[dict], rules: dict) -> list[str]:
    """If the text mentions a surface type but we didn't find it, flag it."""
    missing = []
    text_lower = text.lower()
    found_types = {s["type"] for s in surfaces}
    mention_keywords = rules.get("mention_keywords", {})

    for surface_type, keywords in mention_keywords.items():
        if surface_type in found_types:
            continue
        for kw in keywords:
            if kw.lower() in text_lower:
                missing.append(surface_type)
                break

    return missing


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def _compute_verdict(surfaces: list[dict], rules: dict) -> str:
    if not surfaces:
        return "no_proof"

    surface_types = {s["type"] for s in surfaces}
    verdict_rules = rules.get("verdict_rules", {})

    linked_requires = set(verdict_rules.get("linked_proof_requires_types", ["repo", "dashboard"]))
    linked_min = verdict_rules.get("linked_proof_min_surfaces", 2)

    has_all_linked = linked_requires.issubset(surface_types)
    meets_linked_min = len(surfaces) >= linked_min

    if has_all_linked and meets_linked_min:
        return "linked_proof"

    linked_types = {"repo", "dashboard", "wallet", "polymarket_profile"}
    has_linked_artifact = bool(surface_types & linked_types)
    has_receipt = "fill_receipt" in surface_types
    has_site = "site" in surface_types
    has_docs = "docs" in surface_types

    if has_linked_artifact or has_receipt or has_docs:
        return "partial_proof"

    if has_site and len(surfaces) >= 1:
        return "partial_proof"

    return "no_proof"


def _build_reason(verdict: str, surfaces: list[dict], missing: list[str]) -> str:
    if verdict == "no_proof":
        if missing:
            return f"no auditable proof surface found; text mentions {', '.join(missing)} but none detected"
        return "no auditable proof surface found"

    type_counts = {}
    for s in surfaces:
        type_counts[s["type"]] = type_counts.get(s["type"], 0) + 1

    parts = [f"{count} {stype}" for stype, count in sorted(type_counts.items())]
    surface_summary = ", ".join(parts)

    if verdict == "linked_proof":
        reason = f"linked proof: {surface_summary}"
    else:
        reason = f"partial proof: {surface_summary}"

    if missing:
        reason += f"; missing expected: {', '.join(missing)}"

    return reason


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------

def extract(post: dict, rules_path: Optional[str] = None) -> dict:
    """
    Extract proof surfaces from a moltbook post.

    Args:
        post: dict with keys: text (str), author (str), url (str|None),
              link_targets (list[str]), notes (list[str]|None)
        rules_path: optional path to rules.json override

    Returns:
        dict with keys: verdict, proof_surfaces, missing_expected, reason
    """
    rules = _load_rules(rules_path)

    text = post.get("text", "")
    link_targets = post.get("link_targets") or []
    notes = post.get("notes") or []

    all_text = text
    if notes:
        all_text += "\n" + "\n".join(notes)

    text_urls = _extract_urls(all_text)
    all_urls = list(dict.fromkeys(link_targets + text_urls))

    surfaces = []
    surfaces.extend(_detect_repos(all_urls, rules))
    surfaces.extend(_detect_dashboards(all_urls, rules))
    surfaces.extend(_detect_docs(all_urls, rules))
    surfaces.extend(_detect_polymarket_profiles(all_urls, rules))
    surfaces.extend(_detect_wallets(all_text, rules))
    surfaces.extend(_detect_fill_receipts(all_text, rules))
    surfaces.extend(_detect_sites(all_urls, rules, surfaces))

    missing = _detect_missing_expected(all_text, surfaces, rules)
    verdict = _compute_verdict(surfaces, rules)
    reason = _build_reason(verdict, surfaces, missing)

    return {
        "verdict": verdict,
        "proof_surfaces": surfaces,
        "missing_expected": missing,
        "reason": reason
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extractor.py '<json_input>'")
        print("  or:  echo '<json>' | python extractor.py -")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "-":
        raw = sys.stdin.read()
    else:
        raw = arg

    post = json.loads(raw)
    result = extract(post)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
