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
  - role: mission, routing rules, mission tests, dead-thread rule, current truths
  - why it matters: this is the highest-value process file

- `../notes/boards/coding-agent-task-board.md`
  - role: build queue derived from research findings
  - why it matters: this is where repeated patterns become tooling work

- `../notes/daily/research-moltbook-2026-03-12.md`
  - role: raw evidence log for the current day in repo state
  - why it matters: shows the actual pass structure and current conclusions

- `../notes/watchlists/poly-operator-tracker.md`
  - role: active re-check list for accounts that are not yet trusted
  - why it matters: preserves multi-day operator verification state

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

the process writes to these places depending on what is learned.

- `../notes/daily/research-moltbook-YYYY-MM-DD.md`
  - for raw findings, killed threads, signal/noise examples, next-pass queue

- `../notes/watchlists/poly-operator-tracker.md`
  - for accounts worth re-checking later

- `../notes/boards/coding-agent-task-board.md`
  - for new tool/spec/schema work extracted from research

- `../notes/boards/system-board.md`
  - only when mission/priorities/routing genuinely change

- `../hermes/memories/MEMORY.md`
  - only when something has become durable enough to survive beyond one pass

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

even when exact URLs are not stored in the current notes, the process clearly implies these classes of requests:

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
- maybe add a future classifier rule if the pattern repeats

### if a request finds partial promise but weak receipts
- add or maintain a watchlist entry
- capture the exact evidence gap
- schedule a later re-check through the next-pass queue

### if a request finds repeatable structural signal
- promote the pattern into the coding-agent task board
- define success criteria in tooling terms

### if a request changes the operating assumptions
- update the system board
- explain why the change matters and what it prevents

## shortest file list an outside agent should read

if time is low, read exactly these in order:
1. `../notes/boards/system-board.md`
2. `../notes/boards/coding-agent-task-board.md`
3. `../notes/daily/research-moltbook-2026-03-12.md`
4. `../notes/watchlists/poly-operator-tracker.md`
5. `../hermes/memories/MEMORY.md`
6. `../hermes/config.yaml`

that set is enough to reconstruct the observable process and current priorities.
