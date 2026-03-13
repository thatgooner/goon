# interaction surface

this file answers two things:
- which local files the moltbook process interacts with
- which outside systems, sites, or request types the process is expected to touch

## local file interaction map

### primary canonical files

these are the files an outside agent must read to understand the active process.

- `../AGENTS.md`
  - role: top-level onboarding for any agent entering the repo
  - why it matters: defines the two-agent split and read order

- `../notes/README.md`
  - role: rules for low-context agents working in notes
  - why it matters: defines promotion discipline and archive policy

- `../notes/boards/system-board.md`
  - role: mission, routing rules, mission tests, dead-thread rule, operational rules, sync protocol, current truths
  - why it matters: this is the highest-value process file

- `../notes/boards/coding-agent-task-board.md`
  - role: build queue with full spec fields (sample_inputs, input/output format, testable_acceptance)
  - why it matters: this is where repeated patterns become tooling work. tasks without spec fields are `needs_spec` and cannot be picked up.

- `../notes/daily/research-moltbook-YYYY-MM-DD.md`
  - role: raw evidence log with mission gates, delta tracking, classifier rules, and sample data
  - why it matters: shows the actual pass structure, mission compliance, and current conclusions

- `../notes/watchlists/poly-operator-tracker.md`
  - role: active re-check list for accounts that are not yet trusted
  - why it matters: preserves multi-day operator verification state

### automation and sync files

- `../.cursor/rules/code-worker.mdc`
  - role: Cursor agent rule for code-worker automation
  - why it matters: defines the 1-hour cron cycle protocol, file ownership, and commit conventions

- `../scripts/code-worker-prompt.md`
  - role: trigger prompt for Cursor cloud agent cron
  - why it matters: the exact instruction that starts each code-worker cycle

- `../logs/code-worker/YYYY-MM-DD-HH.md`
  - role: per-cycle progress logs from code-worker
  - why it matters: shows what was built, test results, and blockers. readable at a glance for overnight review.

### secondary process files

- `../README.md`
  - role: human-facing repo overview
  - use: confirms structure and starting points

- `../CHANGELOG.md`
  - role: historical record of major repo/process changes
  - use: shows when onboarding structure and exports were added

- `../hermes/memories/MEMORY.md`
  - role: compressed durable learnings across sessions
  - use: preserves recurring truths such as "moltbook mostly noise"

- `../hermes/memories/USER.md`
  - role: user style/opsec constraints
  - use: matters for messaging and interpretation boundaries, not core research evidence

- `../hermes/config.yaml`
  - role: runtime config for model, tools, platforms, and personality
  - use: tells an external agent what environment gooner runs under

- `../scripts/gooner-export-prompt.md`
  - role: export instructions for syncing gooner state into repo
  - use: relevant when a coding-agent needs deeper environment parity

## write targets

### gooner writes to
- `../notes/daily/research-moltbook-YYYY-MM-DD.md` — raw findings, mission gates, delta, classifier rules, sample data, retro
- `../notes/watchlists/poly-operator-tracker.md` — accounts worth re-checking
- `../notes/boards/coding-agent-task-board.md` — new tasks with full spec fields (append only, do not modify code-worker status changes)
- `../notes/boards/system-board.md` — only when mission/priorities/routing genuinely change
- `../hermes/memories/MEMORY.md` — only when something has become durable enough to survive beyond one pass

### code-worker writes to
- `../tools/<task-name>/` — tool directories (README + code + tests)
- `../logs/code-worker/YYYY-MM-DD-HH.md` — cycle logs
- `../notes/boards/coding-agent-task-board.md` — status updates only (queued -> in_progress -> done)

### neither writes to (read-only)
- `../notes/boards/system-board.md` — only user-initiated changes

## external request surface

this is the outside world the process touches or is expected to touch.

### 1. moltbook
- purpose: primary upstream research surface
- request type: page fetches, timeline/profile inspection, reply inspection, linked-post inspection
- trust level: untrusted by default
- what is extracted:
  - signal themes
  - noise patterns
  - candidate account names
  - claims that need receipts
  - concrete sample data for classifier development

### 2. linked evidence behind moltbook posts
- examples:
  - github repos
  - dashboards
  - docs
  - wallet references
  - methodology writeups
- purpose: verify whether a claim has a proof path
- request type: ordinary web fetches or browser visits
- trust level: still untrusted until checked

### 3. polymarket / operator-adjacent surfaces
- purpose: confirm whether any claimed operator edge has receipts
- request type: reading public pages, checking whether workflows are explicit and reproducible
- trust level: not trusted unless concrete evidence exists

### 4. agent/tooling infrastructure surfaces
- examples from repo state:
  - github for repos and code receipts
  - cloudflare browser rendering API exists in saved skill knowledge, but is not shown as the canonical current moltbook loop
- purpose: support verification or future tooling
- request type: browser fetches, API calls, repository inspection

## concrete external request classes already implied by current state

- fetch a moltbook profile or post
- inspect a comment thread for repeated spam or fake-expert patterns
- open a linked repo or dashboard from a candidate post
- check whether a candidate exposes methodology, wallet evidence, or reproducible receipts
- revisit a tracked account for new receipts

## request classes not yet evidenced as mature or trusted

current repo state does not show a mature authenticated data pipeline for:
- direct moltbook API ingestion
- wallet-tracking automation
- automated polymarket execution ingestion
- private/internal account data

right now the process is closer to evidence-first reconnaissance than to automated market intelligence.

## known decision outputs per request type

### if a request finds only noise
- write a short kill or ignore note in the daily log
- do not promote the account
- capture the noise pattern as a classifier rule candidate

### if a request finds partial promise but weak receipts
- add or maintain a watchlist entry
- capture the exact evidence gap
- schedule a later re-check through the next-pass queue

### if a request finds repeatable structural signal
- promote the pattern into the coding-agent task board
- define success criteria in tooling terms with full spec fields

### if a request changes the operating assumptions
- update the system board
- explain why the change matters and what it prevents

## shortest file list an outside agent should read

if time is low, read exactly these in order:
1. `../notes/boards/system-board.md`
2. `../notes/boards/coding-agent-task-board.md`
3. latest file in `../notes/daily/`
4. `../notes/watchlists/poly-operator-tracker.md`
5. `../.cursor/rules/code-worker.mdc`
6. latest files in `../logs/code-worker/`
7. `../hermes/memories/MEMORY.md`

that set is enough to reconstruct the observable process, current priorities, and overnight progress.
