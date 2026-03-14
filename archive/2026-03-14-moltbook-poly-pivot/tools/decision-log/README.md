# decision-log

Unified logging for decisions, silence events, and agent handoffs. Replaces 3 separate schemas (trust instrumentation, silence logging, escalation receipts) with one append-only JSONL tool.

**Mission:** M4 (orchestration)

## what it does

- Logs 3 types of entries: **decision**, **silence**, **handoff**
- Each entry gets a unique ID and UTC timestamp
- Entries append to a JSONL file (one JSON object per line)
- Supports querying by field and resolving entries
- Round-trip serialize/deserialize preserves all fields including nested types

## entry types

| Type | Required detail fields | Use case |
|------|----------------------|----------|
| `decision` | `options`, `chose`, `reason` | Should X be upgraded/kept/killed? |
| `silence` | `threshold`, `result`, `action_taken`, `reason` | Checked X timeline, nothing met threshold |
| `handoff` | `intent`, `from`, `to` | Agent A needs agent B to do something |

## input format

```json
{ "type": "decision"|"silence"|"handoff", "subject": "str", "detail": {} }
```

## output format

```json
{ "id": "str", "type": "str", "timestamp": "str", "subject": "str", "detail": {}, "resolution": "str|null" }
```

## run instructions (Ubuntu)

No dependencies beyond Python 3.6+.

### as a library

```python
from decision_log import DecisionLog

log = DecisionLog("decisions.jsonl")

# log a decision
entry = log.add({
    "type": "decision",
    "subject": "TheBotcave",
    "detail": {"options": ["upgrade", "keep", "kill"], "chose": "keep", "reason": "still no receipts"}
})

# log a silence event
log.add({
    "type": "silence",
    "subject": "TheBotcave",
    "detail": {"threshold": "new repo or dashboard", "result": "3 posts, all commentary", "action_taken": False, "reason": "no receipts"}
})

# log a handoff
log.add({
    "type": "handoff",
    "subject": "suspicious skill X",
    "detail": {"intent": "audit skill X", "from": "gooner", "to": "code-worker"}
})

# query
results = log.query(subject="TheBotcave")

# resolve
log.resolve(entry["id"], "kept on watch — no new receipts after 7 days")

# read all
all_entries = log.read_all()
```

### CLI

```bash
# add a decision
python3 decision_log.py decisions.jsonl decision TheBotcave '{"options":["upgrade","keep","kill"],"chose":"keep","reason":"still no receipts"}'

# add a silence event
python3 decision_log.py decisions.jsonl silence TheBotcave '{"threshold":"new repo or dashboard","result":"3 posts","action_taken":false,"reason":"no receipts"}'

# add a handoff
python3 decision_log.py decisions.jsonl handoff "suspicious skill" '{"intent":"audit skill X","from":"gooner","to":"code-worker"}'

# query
python3 decision_log.py decisions.jsonl --query subject=TheBotcave

# resolve
python3 decision_log.py decisions.jsonl --resolve <id> "confirmed after review"

# list all
python3 decision_log.py decisions.jsonl --list
```

### run tests

```bash
cd tools/decision-log
python3 -m unittest test_decision_log -v
```

## design

- Append-only JSONL for corruption resistance (each line is a complete JSON object)
- Resolve rewrites via atomic temp-file rename (`os.replace`)
- No external dependencies — stdlib only
- Compact JSON serialization (no extra whitespace) to keep file size small
- IDs are 12-char hex from UUID4 — collision probability negligible for expected volumes
