# tools

code-worker build work lives here.

active lane: `purr` memory infrastructure.

## planned tools
- `memory-ledger/` — canonical memory objects, lifecycle states, Supabase-ready schema/migrations
- `memory-candidate-extractor/` — pull structured memory candidates from normal conversation
- `memory-context-packer/` — choose the right memory under a fixed prompt budget
- `feedback-orchestrator/` — decide ask-now vs defer vs silent-store vs drop
- `memory-review-queue/` — schedule memory verification checks without spamming the user

## conventions
- each tool in its own directory with its own README
- python preferred, keep dependencies minimal
- if Supabase is involved, include schema/migration files and local fixtures
- every tool must have a clear input/output contract
- tests live next to the tool
