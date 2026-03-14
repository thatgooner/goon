# purr memory — 2026-03-14

## pre-pass mission gate
- weekly mission: M1 + M2 + M3
- target objective: pivot the repo away from Moltbook/Polymarket work and define the first real purr-memory build lane
- mapped priority: high

## daily thesis
- purr does not need tool-call flexing in the 1:1 chat. it needs strong memory.
- the real loop is: normal conversation -> candidate memory -> human feedback when needed -> compact retrieval later.

## passes

### 09:00 UTC — pivot definition
- angle: what must exist for purr memory to feel real?
- what was checked: current repo state, old code-worker lane, Hermes memory limitations
- strongest useful idea: split memory into source-of-truth storage, candidate extraction, retrieval packing, and feedback/review loops
- strongest dumb idea: stuffing all remembered context into the prompt every turn
- concrete sample for code-worker: user says `kisa cevap ver` -> should become preference candidate; user later says `hayir daha soguk olsun` -> should revise or reject old memory cleanly
- decisions:
  - Supabase is the source of truth
  - vector is supporting infra only
  - inline clarification is part of the product
  - periodic memory checks should exist but be rate-limited

## post-pass mission audit
- did this pass advance the target objective? yes
- evidence: system board, weekly missions, task board, README, AGENTS, and code-worker rule all pivoted to purr-memory work

## pass delta
- net-new vs yesterday: the repo now has a clean active lane for purr memory infra instead of Moltbook/poly research

## memory truths found today
- memory without lifecycle state will rot
- memory without human correction capture will drift
- memory without prompt-budget control will get expensive fast
- purr should ask for clarification only when the expected value is high enough

## user-feedback moments worth modeling
- explicit correction: `hayir yani ...` style messages should be treated as high-value memory edits
- direct phrasing preference: `kisa cevap ver` should be extracted fast and likely confirmed silently unless conflict appears later
- architecture guidance: `tool call olmayacak, memory lazim` is not fluff; it's mission-level product direction

## prompt-budget notes
- always-hot: core user tone / hard preferences / currently active constraints
- on-demand: episodic details from older sessions
- never dump raw: all session transcripts, low-confidence candidates, stale rejected memory

## build tasks / spec candidates
- memory-ledger
- memory-candidate-extractor
- memory-context-packer
- feedback-orchestrator
- memory-review-queue

## follow-ups
- decide exact Supabase table layout
- decide whether unresolved uncertainty memories should have a separate pack
- decide daily cap for memory verification prompts

## next-pass queue
- let code-worker start with memory-ledger
- then ship extractor + packer
- then tune clarification policy

## process retro
- what consumed the most time: clearing old repo shape so the active lane is readable again
- what should be done differently: keep pivots cleaner and archive faster next time
- did any shipped tool get used? not from the old lane; old tools were archived because the mission changed
