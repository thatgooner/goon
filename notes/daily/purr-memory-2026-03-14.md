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

### 15:30 UTC — Hermes code-grounded hidden logic pass
- angle: stop summarizing Hermes from vibes and read the actual control loops in code
- what was checked: `memory_tool.py`, `run_agent.py`, `hermes_state.py`, `session_search_tool.py`, `context_compressor.py`
- strongest useful idea: `live write / frozen read` + stored prompt snapshot reuse is the real cache-stable behavior pattern to steal
- strongest hidden failure: memory-nudge loop is effectively dead because the turn counter resets every turn before it can accumulate
- other important cracks:
  - `session_search` is not truly per-user scoped
  - child-session hits can get resolved back to the root parent and lose the exact matched detail
  - title numbering is UX lineage, not real episode lineage
  - write-time sanitization exists, but load-time reinjection of existing memory is still a gap
- decisions:
  - Purr needs a frozen session pack but never frozen canonical truth
  - direct corrections need a live override lane
  - every retrieval path must filter by `owner_id` + `purr_id`
  - event-driven extraction/salvage matters more than cute chat-loop nudges
  - lineage must be explicit in data, not inferred from naming

### 17:25 UTC — lifecycle + feedback state-machine pass
- angle: stop talking about `memory lifecycle` like a slogan and lock the actual operating rules
- what was checked: `ily/02`, `ily/05`, `ily/06`, `ily/07`, `notes/boards/purr-alignment-brief.md`, and task-board gaps
- strongest useful idea: keep canonical truth state small (`candidate / confirmed / stale / rejected / superseded`) and layer `review_status`, `contradiction_status`, and `pack_policy` on top
- strongest product rule: if waiting would make the next reply feel fake, that update must hit a live override lane instead of waiting for a session-pack rebuild
- concrete decisions:
  - contradictions should become state transitions, not flat text coexistence
  - challenged memories should be suppressed from the hot factual pack until resolved
  - review prompts need an annoyance budget, not just due dates
  - proactive sends should require stronger trust than normal retrieval and should get quieter when memory is challenged/stale
- repo alignment changes:
  - added `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`
  - updated `ily/README.md`
  - added explicit `memory-lifecycle-and-feedback-state-machine-note` research task to the coding-agent task board before build-order planning

## post-pass mission audit
- did this pass advance the target objective? yes
- evidence: system board, weekly missions, task board, README, AGENTS, and code-worker rule all pivoted to purr-memory work; Hermes teardown now has a code-grounded failure map instead of surface summary only; the repo now also has an explicit lifecycle/feedback state-machine note tying ledger, retrieval, review, contradiction handling, and proactive timing together

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
- decide free-credit / model-routing stance without breaking memory quality
- decide Catnet heartbeat and autonomy boundaries
- decide safe prediction-market event lanes

## next-pass queue
- finish research-first phase before build
- Hermes memory double-dig
- Purr alignment + copy protection
- tool boundary + mobile/webview reality
- Catnet autonomy + market lanes
- then choose first implementation slice

## process retro
- what consumed the most time: clearing old repo shape so the active lane is readable again
- what should be done differently: keep pivots cleaner and archive faster next time
- did any shipped tool get used? not from the old lane; old tools were archived because the mission changed
