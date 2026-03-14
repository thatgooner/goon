#!/usr/bin/env python3
"""
Supply-chain verifier — scans hermes skills, prompts, and payloads for security risk.

Detects: external URL fetches, base64 payloads, shell execution, memory modification,
prompt injection, obfuscation, and missing metadata.

Usage:
    python3 verifier.py <path>                    # scan a file or directory
    python3 verifier.py <path> --json             # JSON output
    python3 verifier.py <path> --severity high    # filter by minimum severity
    python3 verifier.py hermes/skills/ --audit    # full audit mode with summary

Input: file path to a skill directory or single file
Output: { "path": str, "trusted": bool, "issues": [...], "hash_sha256": str }
"""

import hashlib
import json
import os
import re
import sys
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(SCRIPT_DIR, "rules.json")

SEVERITY_ORDER = {"low": 0, "mid": 1, "high": 2}
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".pdf", ".zip", ".gz", ".tar", ".7z", ".rar",
    ".woff", ".woff2", ".ttf", ".eot",
    ".pyc", ".pyo", ".so", ".dll", ".exe",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
}


def load_rules(rules_path=None):
    path = rules_path or RULES_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_file_hash(filepath):
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except (OSError, PermissionError):
        return None
    return h.hexdigest()


def compute_dir_hash(dirpath):
    h = hashlib.sha256()
    for root, dirs, files in sorted(os.walk(dirpath)):
        dirs.sort()
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, dirpath)
            h.update(relpath.encode("utf-8"))
            try:
                with open(fpath, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        h.update(chunk)
            except (OSError, PermissionError):
                h.update(b"<unreadable>")
    return h.hexdigest()


def is_binary(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in BINARY_EXTENSIONS:
        return True
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except (OSError, PermissionError):
        return True
    return False


def read_file_content(filepath):
    if is_binary(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, PermissionError):
        return None


def parse_skill_frontmatter(content):
    """Extract YAML frontmatter from a SKILL.md file."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        try:
            meta = {}
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip()
            return meta
        except Exception:
            return {}


def extract_urls(content):
    """Pull all URLs from content."""
    return re.findall(r'https?://[^\s"\')`\]>]+', content)


def check_url_safety(urls, safe_domains):
    """Check if URLs reference known-safe vs unknown domains."""
    issues = []
    for url in urls:
        domain = re.sub(r'^https?://', '', url).split('/')[0].split(':')[0]
        is_safe = any(
            domain == safe or domain.endswith("." + safe)
            for safe in safe_domains
        )
        if not is_safe:
            issues.append({
                "type": "external_url",
                "detail": f"URL references unknown domain: {url[:200]}",
                "severity": "mid",
            })
    return issues


def scan_patterns(content, patterns, issue_type, severity, context_label=""):
    """Scan content against a list of regex patterns."""
    issues = []
    for pattern in patterns:
        try:
            matches = re.findall(pattern, content, re.IGNORECASE)
        except re.error:
            continue
        if matches:
            sample = matches[0] if isinstance(matches[0], str) else str(matches[0])
            if len(sample) > 120:
                sample = sample[:120] + "..."
            issues.append({
                "type": issue_type,
                "detail": f"{context_label}matched pattern '{pattern}': {sample}",
                "severity": severity,
            })
    return issues


def check_skill_metadata(content, rules):
    """Check SKILL.md for required and recommended metadata."""
    issues = []
    meta = parse_skill_frontmatter(content)

    for field in rules.get("required_skill_metadata", []):
        if field not in meta or not meta[field]:
            issues.append({
                "type": "missing_metadata",
                "detail": f"required metadata field '{field}' is missing from frontmatter",
                "severity": "mid",
            })

    for field in rules.get("recommended_skill_metadata", []):
        if field not in meta or not meta[field]:
            issues.append({
                "type": "missing_metadata",
                "detail": f"recommended metadata field '{field}' is missing from frontmatter",
                "severity": "low",
            })

    return issues


def scan_file(filepath, rules):
    """Scan a single file for supply-chain issues."""
    issues = []
    basename = os.path.basename(filepath)
    content = read_file_content(filepath)

    if content is None:
        return issues

    if basename == "SKILL.md":
        issues.extend(check_skill_metadata(content, rules))

    safe_domains = rules.get("known_safe_domains", [])
    urls = extract_urls(content)
    issues.extend(check_url_safety(urls, safe_domains))

    ext = os.path.splitext(filepath)[1].lower()
    is_script = ext in (".py", ".sh", ".js", ".ts", ".rb", ".pl")
    is_config = ext in (".yaml", ".yml", ".toml", ".ini", ".cfg", ".json")

    if is_script:
        issues.extend(scan_patterns(
            content, rules.get("shell_exec_patterns", []),
            "shell_exec", "high",
        ))
        issues.extend(scan_patterns(
            content, rules.get("base64_patterns", []),
            "base64_payload", "high",
        ))
        issues.extend(scan_patterns(
            content, rules.get("obfuscation_patterns", []),
            "obfuscation", "high",
        ))
        issues.extend(scan_patterns(
            content, rules.get("file_write_patterns", []),
            "file_write", "mid",
        ))
        issues.extend(scan_patterns(
            content, rules.get("credential_access_patterns", []),
            "credential_access", "mid",
        ))

    if is_script:
        issues.extend(scan_patterns(
            content, rules.get("memory_modification_patterns", []),
            "memory_modification", "high",
        ))
        issues.extend(scan_patterns(
            content, rules.get("prompt_injection_patterns", []),
            "prompt_injection", "high",
        ))
    else:
        issues.extend(scan_patterns(
            content, rules.get("memory_modification_patterns", []),
            "memory_modification", "low",
        ))
        issues.extend(scan_patterns(
            content, rules.get("prompt_injection_patterns", []),
            "prompt_injection", "mid",
        ))

    return issues


def scan_path(target_path, rules):
    """Scan a file or directory and return structured results."""
    target_path = os.path.abspath(target_path)

    if not os.path.exists(target_path):
        return {
            "path": target_path,
            "trusted": False,
            "issues": [{"type": "not_found", "detail": "path does not exist", "severity": "high"}],
            "hash_sha256": "",
        }

    all_issues = []

    if os.path.isfile(target_path):
        all_issues.extend(scan_file(target_path, rules))
        file_hash = compute_file_hash(target_path)
    else:
        for root, dirs, files in os.walk(target_path):
            dirs.sort()
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                file_issues = scan_file(fpath, rules)
                relpath = os.path.relpath(fpath, target_path)
                for issue in file_issues:
                    issue["file"] = relpath
                all_issues.extend(file_issues)
        file_hash = compute_dir_hash(target_path)

    deduped = _dedupe_issues(all_issues)

    has_high = any(i["severity"] == "high" for i in deduped)
    trusted = not has_high

    return {
        "path": target_path,
        "trusted": trusted,
        "issues": deduped,
        "hash_sha256": file_hash or "",
    }


def _dedupe_issues(issues):
    """Remove exact duplicate issues (same type+detail+severity+file)."""
    seen = set()
    result = []
    for issue in issues:
        key = (issue.get("type"), issue.get("detail"), issue.get("severity"), issue.get("file", ""))
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result


def filter_by_severity(issues, min_severity):
    """Filter issues to only include those at or above min_severity."""
    min_level = SEVERITY_ORDER.get(min_severity, 0)
    return [i for i in issues if SEVERITY_ORDER.get(i["severity"], 0) >= min_level]


def audit_directory(target_path, rules, min_severity="low"):
    """Run a full audit across a directory, returning per-subdirectory results."""
    target_path = os.path.abspath(target_path)
    results = []

    if not os.path.isdir(target_path):
        return [scan_path(target_path, rules)]

    entries = sorted(os.listdir(target_path))
    for entry in entries:
        entry_path = os.path.join(target_path, entry)
        if entry.startswith("."):
            continue
        result = scan_path(entry_path, rules)
        if min_severity != "low":
            result["issues"] = filter_by_severity(result["issues"], min_severity)
            result["trusted"] = not any(
                i["severity"] == "high" for i in result["issues"]
            )
        results.append(result)

    return results


def format_human(result):
    """Format a single scan result for human reading."""
    lines = []
    path_display = result["path"]
    status = "TRUSTED" if result["trusted"] else "UNTRUSTED"
    lines.append(f"[{status}] {path_display}")
    lines.append(f"  hash: {result['hash_sha256'][:16]}...")

    if not result["issues"]:
        lines.append("  no issues found")
    else:
        high = [i for i in result["issues"] if i["severity"] == "high"]
        mid = [i for i in result["issues"] if i["severity"] == "mid"]
        low = [i for i in result["issues"] if i["severity"] == "low"]
        lines.append(f"  issues: {len(high)} high, {len(mid)} mid, {len(low)} low")
        for issue in result["issues"]:
            sev = issue["severity"].upper()
            file_prefix = f" ({issue['file']})" if "file" in issue else ""
            lines.append(f"  [{sev}] {issue['type']}{file_prefix}: {issue['detail'][:120]}")

    return "\n".join(lines)


def format_audit_summary(results):
    """Format audit results as a human-readable summary."""
    lines = []
    total = len(results)
    trusted = sum(1 for r in results if r["trusted"])
    untrusted = total - trusted
    total_issues = sum(len(r["issues"]) for r in results)
    total_high = sum(1 for r in results for i in r["issues"] if i["severity"] == "high")
    total_mid = sum(1 for r in results for i in r["issues"] if i["severity"] == "mid")
    total_low = sum(1 for r in results for i in r["issues"] if i["severity"] == "low")

    lines.append(f"=== AUDIT SUMMARY ===")
    lines.append(f"scanned: {total} entries")
    lines.append(f"trusted: {trusted} | untrusted: {untrusted}")
    lines.append(f"issues:  {total_high} high, {total_mid} mid, {total_low} low ({total_issues} total)")
    lines.append("")

    for r in results:
        if not r["trusted"]:
            lines.append(format_human(r))
            lines.append("")

    if untrusted == 0:
        lines.append("all entries passed — no high-severity issues detected")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)

    target = args[0]
    json_mode = "--json" in args
    audit_mode = "--audit" in args
    min_severity = "low"
    if "--severity" in args:
        idx = args.index("--severity")
        if idx + 1 < len(args):
            min_severity = args[idx + 1]

    rules_file = None
    if "--rules" in args:
        idx = args.index("--rules")
        if idx + 1 < len(args):
            rules_file = args[idx + 1]

    rules = load_rules(rules_file)

    if audit_mode:
        results = audit_directory(target, rules, min_severity)
        if json_mode:
            print(json.dumps(results, indent=2))
        else:
            print(format_audit_summary(results))
    else:
        result = scan_path(target, rules)
        if min_severity != "low":
            result["issues"] = filter_by_severity(result["issues"], min_severity)
            result["trusted"] = not any(i["severity"] == "high" for i in result["issues"])

        if json_mode:
            print(json.dumps(result, indent=2))
        else:
            print(format_human(result))

    has_high = False
    if audit_mode:
        has_high = any(not r["trusted"] for r in results)
    else:
        has_high = not result["trusted"]

    sys.exit(1 if has_high else 0)


if __name__ == "__main__":
    main()
