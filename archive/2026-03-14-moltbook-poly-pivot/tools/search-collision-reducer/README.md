# search-collision-reducer

Prefilter for Moltbook keyword search results. Downranks results that matched only because the search term overlaps with the author's username or a generic token, and penalizes repeated already-seen authors.

Serves M2 (research support) + M3 (quality filter).

## problem

Moltbook keyword search collapses into username/token collisions:
- `py-clob-client` → random `client`-named accounts
- `wallet xray` → wallet-named agents with no relevant content
- `market making agent` → marketing junk
- `prediction market repo` → same old names (Jaris, Lona) repeating

This tool scores each result on relevance, collision risk, and author novelty, then ranks and filters so gooner can focus on actual signal.

## install

None. Python 3.10+ stdlib only.

## usage

### library

```python
from reducer import reduce_collisions

data = {
    "query": "py-clob-client",
    "results": [
        {
            "author": "client_helper_bot",
            "text": "Hey everyone! Love this community!",
            "url": "https://moltbook.com/post/aaa1",
            "link_targets": []
        },
        {
            "author": "jaris_trader",
            "text": "Used py-clob-client on the CLOB. Fills were terrible.",
            "url": "https://moltbook.com/post/aaa2",
            "link_targets": ["https://github.com/Polymarket/py-clob-client"]
        }
    ],
    "seen_authors": []
}

result = reduce_collisions(data)
# result["ranked_results"] is sorted best-first
# result["summary"] has discard counts
```

### CLI

```bash
# from file
python3 reducer.py input.json

# from stdin
cat input.json | python3 reducer.py -

# with custom rules
python3 reducer.py input.json custom_rules.json
```

## input format

```json
{
  "query": "py-clob-client",
  "results": [
    {
      "author": "some_user",
      "text": "post body text",
      "url": "https://moltbook.com/post/...",
      "link_targets": ["https://github.com/..."]
    }
  ],
  "seen_authors": ["Jaris", "Lona"]
}
```

## output format

```json
{
  "ranked_results": [
    {
      "author": "jaris_trader",
      "url": "https://moltbook.com/post/...",
      "relevance_score": 0.95,
      "collision_score": 0.0,
      "novelty_score": 1.0,
      "keep": true,
      "reason": "exact query phrase found in body text"
    }
  ],
  "summary": {
    "discarded_collisions": 1,
    "discarded_seen": 0
  }
}
```

## scoring

Three components, combined with configurable weights:

| component | what it measures | weight |
|-----------|-----------------|--------|
| relevance | how well the query matches body text / link targets | 0.50 |
| collision | how much the match comes from username overlap only | -0.30 |
| novelty | whether the author is fresh or already-seen | 0.20 |

**combined = (relevance × 0.50) - (collision × 0.30) + (novelty × 0.20)**

### relevance tiers

| condition | score |
|-----------|-------|
| exact query phrase in body text | 0.95 |
| exact query phrase in link targets | 0.90 |
| all query tokens in body/links | 0.80 |
| most query tokens (≥60%) in body/links | 0.60 |
| some query tokens in body/links | 0.40 |
| no query tokens in body or links | 0.05 |

### collision detection

Tokenizes the query and the username. If query tokens appear in the username but NOT in the body text or link targets, that's a collision. Severity scales with the ratio of username-only tokens.

### novelty scoring

- fresh author: 1.0
- seen author with new signal content (link targets or signal markers like API/CLOB/repo references): 0.4
- seen author with only query-token echo (no real new content): 0.1

Important: for seen authors, merely containing query tokens in the body does NOT count as new content — those tokens are why they matched the search. New content means signal markers or link targets.

### discard rules

A result gets `keep=false` when:
1. **hard collision**: collision score ≥ 0.75
2. **soft collision**: any username collision + very low body relevance
3. **stale seen author**: seen author with no new content and relevance below 0.80
4. **low combined score**: combined score below 0.30

## rules.json tuning guide

All thresholds, weights, and patterns live in `rules.json`. Key sections:

- **scoring_weights**: adjust how much relevance/collision/novelty matter
- **thresholds**: `keep_min_combined` (min score to keep), `collision_discard` (hard collision cutoff)
- **relevance_bonuses**: score for each match tier
- **collision_scores**: score for each collision tier
- **novelty_scores**: fresh vs seen author scores
- **stop_words**: words to skip when tokenizing queries
- **signal_boost_patterns**: keywords that indicate genuine signal (repo links, API references, evidence markers)

To tune: edit `rules.json`, re-run tests to verify nothing breaks.

## tests

```bash
cd tools/search-collision-reducer
python3 -m unittest test_reducer.py -v
```

62 tests covering:
- all 3 task board sample inputs
- relevance scoring tiers
- collision detection (full, partial, none)
- novelty scoring (fresh, seen with new content, stale)
- output format compliance
- edge cases (empty results, empty query, all seen authors, stop-word-only queries)
- JSON serialization round-trip
- ranking order verification
- collision bait discard with explicit reasons
- seen + collision combo penalties
