# feed-triage-scorer

Combines spam detection with signal scoring into one reusable triage pass. This is the main filter gooner uses against moltbook feed items.

## what it does

Takes a moltbook post and produces:
- **spam_score** (0-1): how spammy/noisy the post is
- **signal_score** (0-1): how much real evidence/value it contains
- **reasons**: list of matched rules and context modifiers
- **action**: `read` | `skip` | `watchlist` | `promote`

## input format

```json
{
  "text": "post body text",
  "author": "username",
  "url": "https://... or null",
  "has_links": true,
  "link_targets": ["github.com/user/repo"]
}
```

`has_links` and `link_targets` are optional — derived from text/url if missing.

## output format

```json
{
  "signal_score": 0.55,
  "spam_score": 0.1,
  "reasons": ["signal rules: api_reference, concrete_numbers", "action=watchlist (spam=0.10, signal=0.55)"],
  "action": "watchlist"
}
```

## action logic

| condition | action |
|-----------|--------|
| spam_score >= 0.7 | skip |
| signal_score >= 0.6 and spam_score <= 0.3 | promote |
| signal_score >= 0.4 and spam_score <= 0.5 | watchlist |
| signal_score >= 0.2 and spam_score <= 0.6 | read |
| spam_score > signal_score | skip |
| fallback | read |

## usage

### python import

```python
from scorer import score_post, score_batch

result = score_post({
    "text": "ran this against polymarket CLOB API...",
    "author": "builder",
    "url": None,
    "has_links": True,
    "link_targets": ["github.com/example/pm-bot"]
})
print(result["action"])  # "promote"
```

### CLI

```bash
# single post or batch from JSON file
python3 scorer.py input.json

# interactive demo with built-in samples
python3 scorer.py
```

### batch scoring

```python
posts = [{"text": "...", "author": "...", "url": None}, ...]
results = score_batch(posts)
for r in results:
    print(f"{r['action']}: spam={r['spam_score']:.2f} signal={r['signal_score']:.2f}")
```

## what it detects

### spam patterns (21 rules)
- generic praise, emoji floods, LFG/WAGMI hype
- fake expert walls (long text, no links, no numbers)
- promo spam tokens (MBC-20, airdrops, mint spam)
- direct spam keywords (buy now, guaranteed returns, DM for details)
- thread hijack promo, RSS promo
- service manifest solicitation (rates + off-platform contact)
- trading aesthetic without method (vibes, no proof)
- duplicate launch spam (install commands, no repo)
- performance flex without proof surface
- recycled profit anecdotes, buzzword soup

### signal indicators (12 rules)
- GitHub/GitLab repo links, repo references
- API references (CLOB, funding rate, py-clob-client)
- concrete numbers (spread thresholds, fill prices)
- first-person execution receipts
- wallet disclosures, dashboard links
- methodology detail (step-by-step)
- falsifiable claims (market-skip rules, heuristics)
- trading methodology terms (position sizing, Kelly criterion)
- security analysis content
- cross-market framework (prediction market odds → asset exposure)

### context modifiers
- **evidence link boost**: posts with repo/dashboard links get signal boost + spam dampening
- **security context protection**: install commands in security warnings are NOT treated as promo
- **theory-without-receipts penalty**: trading theory with venue names but no proof gets signal reduced
- **repo link bonus**: explicit repo URLs in link_targets get extra signal

## tuning

Edit `rules.json` to add/remove/reweight patterns. Gooner can update this file directly.

Each rule has: `id`, `type` (regex | keyword_list | heuristic), pattern/keywords, `weight`.

Action thresholds are also in `rules.json` under `action_thresholds`.

## running tests

```bash
python3 -m unittest test_scorer.py -v
```

40 tests covering task board acceptance, gooner's daily note samples, edge cases, action derivation, batch scoring, and output format.

## dependencies

None. Python 3 stdlib only.

## how it relates to other tools

- Incorporates spam patterns from `tools/spam-classifier/` (same rule types, reweighted for triage context)
- Can be used alongside `tools/commenter-tracker/` — this tool scores posts, commenter-tracker scores comment accounts
- Together they form the M3 quality filter layer
