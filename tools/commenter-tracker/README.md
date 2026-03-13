# commenter-pattern-tracker

Detects repeated phrase spam, burst posting, low-substance generic praise, and coordinated reply sludge **per account** across a batch of comments. Part of M3 (quality filter).

## what it catches

- **repeated phrases**: same author posting identical or near-identical text (Jaccard similarity > 0.6) across multiple comments
- **burst activity**: N+ comments within a configurable time window (default: 3 in 15 minutes)
- **low substance**: generic praise, emoji-heavy, very short, no technical terms or links
- **post spread**: commenting on many distinct posts in a short time
- **generic praise density**: emoji/exclamation/praise word density per comment

Each component contributes to a **spam_score** (0-1) via tunable weights in `rules.json`.

## usage

### CLI

```bash
python3 tracker.py input.json              # pretty-print to stdout
python3 tracker.py input.json -o out.json  # write to file
```

### library

```python
from tracker import analyze_comments

result = analyze_comments({
    "comments": [
        {"author": "bot", "text": "Amazing work! 🔥", "post_url": "p/1", "timestamp": "2026-03-13T10:00:00Z"},
        {"author": "bot", "text": "Amazing work! 🔥", "post_url": "p/2", "timestamp": "2026-03-13T10:02:00Z"},
    ]
})
```

## I/O format

### input

```json
{
  "comments": [
    {
      "author": "hype_bot_99",
      "text": "Amazing work! 🔥",
      "post_url": "https://moltbook.com/post/abc123",
      "timestamp": "2026-03-13T10:00:00Z"
    }
  ]
}
```

### output

```json
{
  "accounts": [
    {
      "author": "hype_bot_99",
      "comment_count": 5,
      "repeated_phrases": ["amazing work"],
      "touched_posts": ["https://moltbook.com/post/0", "https://moltbook.com/post/1"],
      "burst_windows": [
        {"start": "2026-03-13T10:00:00+00:00", "end": "2026-03-13T10:08:00+00:00", "count": 5}
      ],
      "spam_score": 0.85
    }
  ]
}
```

Accounts are sorted by `spam_score` descending (spammiest first).

## detection logic

### spam_score components

| component | weight | what it measures |
|-----------|--------|-----------------|
| repeated_phrase_ratio | 0.30 | fraction of comments that are near-dupes of another from same author |
| burst_ratio | 0.20 | fraction of comments inside burst windows |
| low_substance_ratio | 0.25 | fraction of comments flagged as generic/low-substance |
| post_spread_factor | 0.10 | many distinct posts commented on in short time |
| generic_praise_density | 0.15 | average emoji/exclamation/praise density |

All weights are in `rules.json` and can be tuned without editing code.

### phrase similarity

Uses Jaccard similarity on lowercased word tokens (emoji stripped). Threshold default: 0.6.

### burst detection

Sliding window: default 15 minutes, minimum 3 comments. Non-overlapping burst windows reported.

## tuning

Edit `rules.json` to adjust:
- similarity thresholds
- burst window size and minimum count
- generic praise patterns (regex)
- signal terms that exempt a comment from low-substance flagging
- spam_score weights
- post spread thresholds

## tests

```bash
python3 -m unittest test_tracker.py -v
```

Covers: hype_bot_99 (>0.7), legit_builder (<0.3), repeated phrases, near-duplicates, burst windows, mixed batches, edge cases, simoncaleb essay-wall pattern, thread hijack, ClawV6 generic praise, g1-node service manifest, timestamp formats, CLI roundtrip.

## deps

Python 3.8+ stdlib only. No external packages.
