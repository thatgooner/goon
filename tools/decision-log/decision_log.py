#!/usr/bin/env python3
"""
decision-log — unified logging for decisions, silence events, and agent handoffs.

Replaces 3 separate schemas (trust instrumentation, silence logging, escalation
receipts) with one tool that appends structured entries to a JSONL file.

Usage:
    # As a library
    from decision_log import DecisionLog
    log = DecisionLog("decisions.jsonl")
    entry = log.add({
        "type": "decision",
        "subject": "TheBotcave",
        "detail": {"options": ["upgrade","keep","kill"], "chose": "keep", "reason": "still no receipts"}
    })

    # CLI
    python3 decision_log.py decisions.jsonl decision TheBotcave '{"options":["upgrade","keep","kill"],"chose":"keep","reason":"still no receipts"}'
    python3 decision_log.py decisions.jsonl --query subject=TheBotcave
    python3 decision_log.py decisions.jsonl --resolve <id> "kept on watch — no new receipts after 7 days"
"""

import json
import sys
import uuid
import os
from datetime import datetime, timezone
from typing import Optional


VALID_TYPES = {"decision", "silence", "handoff"}

REQUIRED_DETAIL_FIELDS = {
    "decision": {"options", "chose", "reason"},
    "silence": {"threshold", "result", "action_taken", "reason"},
    "handoff": {"intent", "from", "to"},
}


def _generate_id() -> str:
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_entry(data: dict) -> list:
    """Validate an input entry. Returns list of error strings (empty = valid)."""
    errors = []

    if "type" not in data:
        errors.append("missing required field: type")
        return errors

    entry_type = data["type"]
    if entry_type not in VALID_TYPES:
        errors.append(f"invalid type '{entry_type}', must be one of: {sorted(VALID_TYPES)}")
        return errors

    if "subject" not in data or not isinstance(data["subject"], str) or not data["subject"].strip():
        errors.append("missing or empty required field: subject")

    if "detail" not in data or not isinstance(data["detail"], dict):
        errors.append("missing or non-dict required field: detail")
        return errors

    required = REQUIRED_DETAIL_FIELDS.get(entry_type, set())
    missing = required - set(data["detail"].keys())
    if missing:
        errors.append(f"detail missing required fields for type '{entry_type}': {sorted(missing)}")

    return errors


class DecisionLog:
    """Append-only decision log backed by a JSONL file."""

    def __init__(self, path: str):
        self.path = path

    def add(self, data: dict) -> dict:
        """Validate input, enrich with id/timestamp, append to file, return entry."""
        errors = _validate_entry(data)
        if errors:
            raise ValueError("; ".join(errors))

        entry = {
            "id": _generate_id(),
            "type": data["type"],
            "timestamp": _now_iso(),
            "subject": data["subject"],
            "detail": data["detail"],
            "resolution": None,
        }

        self._append(entry)
        return entry

    def resolve(self, entry_id: str, resolution: str) -> dict:
        """Mark an existing entry as resolved. Rewrites file with updated entry."""
        entries = self.read_all()
        found = None
        for e in entries:
            if e["id"] == entry_id:
                found = e
                break

        if found is None:
            raise KeyError(f"entry not found: {entry_id}")

        found["resolution"] = resolution
        self._rewrite(entries)
        return found

    def read_all(self) -> list:
        """Read all entries from the JSONL file."""
        if not os.path.exists(self.path):
            return []

        entries = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    entries.append(json.loads(stripped))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"corrupt JSONL at line {line_num}: {exc}") from exc
        return entries

    def query(self, **filters) -> list:
        """Query entries by field values. Supports top-level fields only."""
        entries = self.read_all()
        results = []
        for e in entries:
            if all(e.get(k) == v for k, v in filters.items()):
                results.append(e)
        return results

    def _append(self, entry: dict):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

    def _rewrite(self, entries: list):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n")
        os.replace(tmp, self.path)


def _cli_add(log: DecisionLog, entry_type: str, subject: str, detail_json: str) -> dict:
    detail = json.loads(detail_json)
    return log.add({"type": entry_type, "subject": subject, "detail": detail})


def _cli_query(log: DecisionLog, filter_str: str) -> list:
    pairs = filter_str.split(",")
    filters = {}
    for pair in pairs:
        k, v = pair.split("=", 1)
        filters[k.strip()] = v.strip()
    return log.query(**filters)


def _cli_resolve(log: DecisionLog, entry_id: str, resolution: str) -> dict:
    return log.resolve(entry_id, resolution)


def main():
    if len(sys.argv) < 3:
        print("Usage: decision_log.py <file> <type> <subject> '<detail_json>'")
        print("       decision_log.py <file> --query <key=value,...>")
        print("       decision_log.py <file> --resolve <id> '<resolution>'")
        print("       decision_log.py <file> --list")
        sys.exit(1)

    path = sys.argv[1]
    log = DecisionLog(path)

    if sys.argv[2] == "--query":
        results = _cli_query(log, sys.argv[3])
        for r in results:
            print(json.dumps(r, indent=2))
    elif sys.argv[2] == "--resolve":
        entry = _cli_resolve(log, sys.argv[3], sys.argv[4])
        print(json.dumps(entry, indent=2))
    elif sys.argv[2] == "--list":
        for e in log.read_all():
            print(json.dumps(e, indent=2))
    else:
        entry = _cli_add(log, sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()
