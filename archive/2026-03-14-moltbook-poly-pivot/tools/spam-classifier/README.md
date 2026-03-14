# spam-classifier

Rule-based moltbook post classifier. Separates signal from noise/spam without LLM API keys.

## what it does

Classifies moltbook posts into 4 categories:
- **spam** — intentional promo, token/airdrop spam, scam pitches
- **noise** — generic praise, fake-expert walls, engagement bait, recycled profit anecdotes, performance flexes without proof
- **signal** — linked repos/dashboards, specific API references, concrete numbers, execution receipts, falsifiable claims
- **uncertain** — not enough signal either way, or mixed noise+signal

## usage

```python
from classifier import classify

result = classify({
    "text": "ran this against polymarket CLOB API, here's the repo: github.com/example/pm-bot",
    "author": "builder",
    "url": None
})

# result:
# {
#     "label": "signal",
#     "confidence": 0.95,
#     "matched_rules": ["github_link", "repo_reference", "api_reference", ...],
#     "reason": "signal indicators present (score=2.45); ..."
# }
```

### batch classification

```python
from classifier import classify_batch

results = classify_batch([post1, post2, post3])
```

### CLI

```bash
python3 classifier.py                    # run on built-in samples
python3 classifier.py input.json         # classify from JSON file
```

## input format

```json
{ "text": "post content", "author": "username", "url": "https://..." }
```

`url` can be `null`. If present, it's factored into signal scoring.

## output format

```json
{
    "label": "spam|noise|signal|uncertain",
    "confidence": 0.85,
    "matched_rules": ["generic_praise", "short_hype_only"],
    "reason": "noise patterns detected (score=1.10); noise rules: generic_praise, short_hype_only"
}
```

## how it works

1. Scores the post against noise patterns, spam keywords, and signal indicators from `rules.json`
2. Posts with repo/dashboard links (github, gitlab, dune, etc.) get signal protection — noise is dampened, and these posts are never labeled spam based on noise alone
3. Final label is determined by comparing noise vs signal scores against configurable thresholds
4. Promo-specific noise patterns (token spam, RSS promo) escalate from noise to spam

## rules.json

All patterns live in `rules.json` so gooner can add new patterns without editing Python code.

Rule types:
- **regex** — regular expression matched against post text
- **keyword_list** — list of keywords checked against lowercased text
- **heuristic** — named Python function for complex checks (emoji ratio, fake-expert wall detection, etc.)

Each rule has an `id`, `description`, `weight`, and `type`. Weights accumulate when multiple rules match.

### adding new rules

Add to the appropriate array in `rules.json`:

```json
{
    "id": "my_new_pattern",
    "description": "What this catches",
    "type": "regex",
    "pattern": "(?i)\\bmy pattern\\b",
    "weight": 0.4
}
```

For heuristics, you also need to add the function in `classifier.py` and register it in `_eval_heuristic()`.

## tests

```bash
python3 -m unittest tools/spam-classifier/test_classifier.py -v
```

Test corpus: 25 hand-labeled examples covering task board samples, gooner's daily note samples, and additional variations. Current accuracy: 100% (25/25).

## pattern categories

### noise patterns detected
- generic praise with no implementation detail
- fake-expert walls (long text, zero links/numbers, enterprise buzzwords)
- emoji floods and LFG/WAGMI bait
- crypto/AI buzzword soup
- thread hijack promos
- recycled profit anecdotes from X/Twitter
- performance metric flexes without proof
- install commands without repo links
- meta-question walls with no evidence
- RSS/newsletter promos

### signal indicators
- GitHub/GitLab/Bitbucket repo links
- dashboard links (Dune, Grafana, Google Docs)
- specific API references (CLOB, funding rate, py-clob-client)
- concrete numbers in trading context
- first-person execution receipts
- wallet/transaction disclosures
- step-by-step methodology
- trading methodology terms (max leverage, regime exit, Kelly criterion)
- falsifiable claims/rules

## deps

Python 3.8+, stdlib only. No external packages.
