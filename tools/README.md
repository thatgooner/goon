# tools

codex build work lives here. each tool gets its own directory.

## planned tools (from codex task board)

### high priority
- `supply-chain-verifier/` — provenance, hash, signature checks for skills/prompts/payloads
- `spam-classifier/` — moltbook spam and fake-expert detection
- `trust-schema/` — trust instrumentation schema (trigger, options, delta, blast radius)
- `silence-logger/` — structured silence logging (what was checked, why no action)
- `escalation-receipts/` — durable handoff records with resume tokens
- `commenter-tracker/` — repeated phrase and burst-pattern spam detection

### mid priority
- `feed-scorer/` — signal/spam scoring per post
- `agent-discovery/` — high-quality agent finder with quality filter
- `security-tricks/` — extraction list of operator/security tricks
- `memory-capture/` — high-signal memory selection

### low priority
- `poly-map/` — polymarket niche and copytrading candidate map
- `memory-guardrails/` — drift detection for memory files

## conventions
- each tool in its own directory with its own README
- python preferred, keep dependencies minimal
- every tool must have a clear input/output contract
- tests go in the tool directory
