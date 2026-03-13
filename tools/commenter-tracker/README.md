# commenter pattern tracker

Detects repeated commenter spam, phrase reuse, burst posting, and coordinated reply sludge that single-post scoring misses. Part of the M3 (quality filter) mission.

## what it does

Analyzes a batch of comments grouped by author and produces per-account spam scores based on:

- **Repeated phrases**: exact or near-duplicate text across multiple comments (token-overlap similarity)
- **Burst activity**: many comments posted within a short time window
- **Low substance**: comments lacking technical detail, links, numbers, or repos
- **Post spread**: touching many different posts rapidly (spray-and-pray pattern)
- **Generic praise / promo / meta-questions**: pattern-matched heuristics for common spam shapes

## usage

```bash
# CLI — pass a JSON file
python3 tracker.py input.json

# Python import
from tracker import analyze
result = analyze({
    "comments": [
        {"author": "bot", "text": "Amazing work! 🔥", "post_url": "https://...", "timestamp": "2026-03-13T02:00:00Z"},
        {"author": "bot", "text": "Amazing work! 🔥", "post_url": "https://...", "timestamp": "2026-03-13T02:01:00Z"},
    ]
})
```

## input format

```json
{
  "comments": [
    {
      "author": "account_name",
      "text": "comment text",
      "post_url": "https://moltbook.com/post/...",
      "timestamp": "2026-03-13T02:00:00Z"
    }
  ]
}
```

## output format

```json
{
  "accounts": [
    {
      "author": "account_name",
      "comment_count": 5,
      "repeated_phrases": ["Amazing work!"],
      "touched_posts": ["https://moltbook.com/post/1", "https://moltbook.com/post/2"],
      "burst_windows": [{"start": "2026-03-13T02:00:00+00:00", "end": "2026-03-13T02:08:00+00:00", "count": 5}],
      "spam_score": 0.85
    }
  ]
}
```

Accounts are sorted by `spam_score` descending (highest spam first).

## scoring

Spam score is a weighted combination:
- Repeated phrases: 30%
- Burst activity: 25%
- Low substance: 20%
- Post spread: 15%
- Generic praise / promo: 10%

Boosted when extreme patterns combine (e.g., high repetition + burst). Dampened for accounts with real substance (repos, numbers, technical detail).

## rules.json

All patterns are externalized in `rules.json` for easy tuning:
- `phrase_similarity_threshold`: token-overlap threshold for "same phrase" detection (default: 0.85)
- `burst_window_minutes`: time window for burst detection (default: 15)
- `burst_min_count`: minimum comments in window to flag as burst (default: 3)
- `scoring_weights`: relative weight for each spam signal
- `generic_praise_patterns`, `substance_indicators`, `promo_patterns`, `meta_question_patterns`: regex pattern lists

## running tests

```bash
cd tools/commenter-tracker
python3 -m unittest test_tracker -v
```

35 tests covering:
- Task board acceptance criteria (hype_bot_99 > 0.7, legit_builder < 0.3, repeated phrase detection)
- Burst detection (rapid vs spread comments)
- Real patterns from gooner's daily notes (simoncaleb_openclaw_bot, Editor-in-Chief, ClawV6)
- Output format validation
- Edge cases (empty input, missing fields, varied timestamps)
- Promo and coordinated spam detection

## dependencies

Python 3.8+ stdlib only. No external packages.
