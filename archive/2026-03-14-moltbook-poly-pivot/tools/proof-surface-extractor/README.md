# proof-surface extractor

Detects auditable proof surfaces in moltbook posts and produces a verdict: `no_proof`, `partial_proof`, or `linked_proof`.

## why

Too much pass time gets burned manually deciding whether a post/account has any auditable surface at all. This tool gives gooner a fast extractor for repos, dashboards, wallets, fill receipts, polymarket profiles, docs, and generic sites — plus a clean `no_proof` verdict when nothing real is there.

## usage

### python API

```python
from extractor import extract

result = extract({
    "text": "Polymarket CLOB API is a liquidity desert. Tried to buy NO at $0.22, filled at $0.99.",
    "author": "Jaris",
    "url": "https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92",
    "link_targets": [],
    "notes": None
})
# result["verdict"] == "partial_proof"
# result["proof_surfaces"] includes fill_receipt
```

### CLI

```bash
python3 extractor.py '{"text": "Check our repo", "author": "dev", "url": null, "link_targets": ["https://github.com/dev/tool"], "notes": null}'
```

or pipe:

```bash
echo '{"text": "...", "author": "...", "url": null, "link_targets": [], "notes": null}' | python3 extractor.py -
```

## input format

```json
{
  "text": "post body text",
  "author": "account name",
  "url": "moltbook post URL or null",
  "link_targets": ["https://github.com/...", "https://dune.com/..."],
  "notes": ["optional researcher notes"] 
}
```

## output format

```json
{
  "verdict": "no_proof | partial_proof | linked_proof",
  "proof_surfaces": [
    {"type": "repo", "value": "https://github.com/user/repo", "confidence": 0.9},
    {"type": "fill_receipt", "value": "phrases: filled at, slippage", "confidence": 0.7}
  ],
  "missing_expected": ["dashboard"],
  "reason": "partial proof: 1 fill_receipt, 1 repo; missing expected: dashboard"
}
```

## surface types

| type | what it detects | example |
|------|----------------|---------|
| `repo` | GitHub, GitLab, Bitbucket, Codeberg, HuggingFace repos | `github.com/user/pm-bot` |
| `dashboard` | Dune, Nansen, DeBank, Zapper, Grafana dashboards | `dune.com/user/fills` |
| `wallet` | Ethereum (0x...) addresses in text | `0x742d35Cc...` |
| `polymarket_profile` | Polymarket profile/portfolio URLs | `polymarket.com/profile/0x...` |
| `site` | Non-classified external URLs (not moltbook/twitter) | `lona.agency` |
| `docs` | Documentation sites and /docs paths | `myproject.gitbook.io` |
| `fill_receipt` | Execution language: fills, slippage, PnL, spread heuristics | `filled at $0.99`, `spread >20%` |

## verdict logic

- **`no_proof`**: no surfaces found at all
- **`partial_proof`**: at least one surface (repo, dashboard, wallet, fill receipt, docs, site)
- **`linked_proof`**: repo AND dashboard both present (minimum 2 surfaces total)

## missing_expected

If the text mentions a surface type (e.g. "check our repo") but no matching URL/artifact was found, it appears in `missing_expected`. Useful for catching claims without proof.

## rules.json

All patterns, domains, and thresholds are externalized in `rules.json`. Gooner can tune:
- `repo_domains`, `dashboard_domains`, `docs_domains`, `polymarket_domains`
- `wallet_patterns` (regex per chain)
- `fill_receipt_phrases` and `fill_receipt_patterns`
- `mention_keywords` (triggers missing_expected warnings)
- `verdict_rules` (what qualifies as linked_proof)

## tests

```bash
cd tools/proof-surface-extractor
python3 -m unittest test_extractor -v
```

## dependencies

None — stdlib only (json, re, os, pathlib, urllib.parse).
