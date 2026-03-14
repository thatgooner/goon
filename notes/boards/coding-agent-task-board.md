# coding-agent task board

MISSION CHANGE — READ THIS FIRST:
- old moltbook/poly lane is archived under `archive/2026-03-14-moltbook-poly-pivot/`
- active mission is now `purr` memory infrastructure
- CURRENT PHASE = research first, build later
- if you are code-worker, do not start shipping new tools until the research tasks below are done
- first run helper: `notes/boards/code-worker-first-run-checklist.md`

read `weekly-missions.md` first. every task here must serve an active weekly mission.

priority model:
- high = directly serves this week's missions and is ready now
- parked = valid later work, not for this week

status values: `queued` | `in_progress` | `done` | `blocked`
when code-worker picks a task: set status to `in_progress`, add `picked_cycle: YYYY-MM-DD-HH`

---

## high — research first

### hermes-memory-independent-review
- mission: M1 (Hermes memory teardown)
- why: code-worker needs its own read on Hermes memory, not just borrowed opinions.
- sample_inputs:
  - `tools/memory_tool.py`
  - `tools/session_search_tool.py`
  - `hermes_state.py`
  - `run_agent.py` memory flush / prompt rebuild sections
- input_format: repo paths + docs references in Hermes repo
- output_format: markdown summary in the cycle log covering `what is good`, `why it is good`, `what breaks for purr`, `what to reuse`, `what to avoid`
- testable_acceptance: review must mention frozen prompt snapshot, bounded curated memory, transcript/session search layer, memory nudge + pre-compression flush behavior, session-lineage continuation after compression, and at least 3 concrete limitations for purr.
- status: queued
- owner: code-worker
- pick order: 1

### purr-alignment-independent-brief
- mission: M2 (Purr alignment)
- why: builder must understand the creature before touching infra.
- sample_inputs:
  - `notes/boards/purr-alignment-brief.md`
  - landing copy and product text from user
  - World mini app / webview constraint
- input_format: repo docs + product copy
- output_format: cycle-log summary of `what purr is`, `what purr is not`, `memory implications`, `tone constraints`, `anti-patterns`
- testable_acceptance: brief must explicitly reject `dashboard pet`, `visible tool-call theater`, and `generic wholesome assistant cat`. must explain why memory is the product.
- status: queued
- owner: code-worker
- pick order: 2

### tool-boundary-and-mobile-note
- mission: M3 (tool boundary + mobile reality)
- why: before build, we need a clear stance on whether tools are user-visible and what webview/mobile changes.
- sample_inputs:
  - Purr 1:1 chat experience
  - internal memory maintenance needs
  - World mini app webview/mobile environment
- input_format: product constraints from repo docs
- output_format: cycle-log note with 3 sections: `internal tools`, `user-visible tools`, `mobile/webview constraints`
- testable_acceptance: note must give a direct first-pass answer on user-visible tools and call out server-side persistence + notification/re-entry constraints.
- status: queued
- owner: code-worker
- pick order: 3

### catnet-autonomy-and-market-lanes
- mission: M3 (tool boundary + mobile reality)
- why: Catnet and prediction markets are part of the product thesis now, but they need clean boundaries before build.
- sample_inputs:
  - autonomous Catnet requirement
  - no direct human control over Catnet posting
  - prediction markets with verifiable events only
  - karma/reputation + fee flow back to the human
- input_format: repo briefs + product notes
- output_format: cycle-log note covering `Catnet autonomy model`, `heartbeat/orchestration`, `safe prediction market lanes`, `bad/forbidden lanes`
- testable_acceptance: note must explicitly reject private-human-behavior markets and direct human puppeting of Catnet. must propose at least 3 good early market domains.
- status: queued
- owner: code-worker
- pick order: 4

### prediction-memory-and-proactive-timing-note
- mission: M1 + M3 (Hermes memory teardown + tool boundary/mobile reality)
- why: Purr's `feels one step ahead of me` quality depends on structured pattern memory, bounded prediction hints, and invisible background timing ops — not prompt bloat.
- sample_inputs:
  - `ily/02-purr-app-memory-architecture.md`
  - `ily/05-hermes-memory-behavioral-teardown.md`
  - `ily/06-purr-prediction-and-background-memory-ops.md`
  - `notes/boards/purr-alignment-brief.md`
- input_format: repo docs + memory architecture notes
- output_format: cycle-log note covering `prediction memory kinds`, `horizons`, `retrieval budget`, `background jobs`, `failure modes`
- testable_acceptance: must explicitly define `pattern_signal`, `open_loop`, and `next_action_candidate`; must separate turn-critical hidden ops vs deferred maintenance vs heartbeat jobs; must keep prediction as backend memory signal, not flashy user-facing feature.
- status: queued
- owner: code-worker
- pick order: 5

### memory-lifecycle-and-feedback-state-machine-note
- mission: M1 + M2 + M3 (Hermes memory teardown + Purr alignment + tool boundary/mobile reality)
- why: the repo already knows memory needs lifecycle, correction handling, and review taste, but build order is still too loose until the actual state machine is explicit.
- sample_inputs:
  - `ily/02-purr-app-memory-architecture.md`
  - `ily/05-hermes-memory-behavioral-teardown.md`
  - `ily/06-purr-prediction-and-background-memory-ops.md`
  - `ily/07-hermes-memory-code-grounded-hidden-logic.md`
  - `notes/boards/purr-alignment-brief.md`
- input_format: repo docs + memory architecture notes
- output_format: cycle-log note covering `canonical states`, `ask_now/defer/silent_store/drop rules`, `contradiction handling`, `review cadence`, `retrieval/proactive gating`
- testable_acceptance: must define a small canonical lifecycle, explain how same-session corrections hit a live override lane, define when challenged/stale memories are suppressed from the pack, and give anti-spam review caps.
- status: queued
- owner: code-worker
- pick order: 6

### retrieval-context-packer-and-pack-lifecycle-note
- mission: M1 + M3 (Hermes memory teardown + tool boundary/mobile reality)
- why: the repo now has memory kinds, lifecycle, contradiction handling, and prediction lanes, but the actual bounded pack contract is still the missing bridge between the ledger and the prompt.
- sample_inputs:
  - `ily/02-purr-app-memory-architecture.md`
  - `ily/06-purr-prediction-and-background-memory-ops.md`
  - `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`
  - `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md`
  - `notes/boards/hermes-memory-review.md`
  - `notes/boards/purr-alignment-brief.md`
- input_format: repo docs + Hermes budget discipline read
- output_format: cycle-log note covering `pack artifacts`, `slot caps`, `budget envelopes`, `patch vs rebuild triggers`, `mobile re-entry behavior`
- testable_acceptance: must define separate `session_pack`, `turn_delta_pack`, `reentry_pack`, and `proactive_pack`; must give concrete budget/slot rules; must explain why free-tier cuts should hit throughput/model/proactivity before memory integrity.
- status: queued
- owner: code-worker
- pick order: 7

### session-scope-and-lineage-contract-note
- mission: M1 + M2 + M3 (Hermes memory teardown + Purr alignment + tool boundary/mobile reality)
- why: latest Hermes teardown makes one thing painfully clear — `1 human = 1 purr` only works if identity scope, active session-window scope, and episode lineage are explicit. otherwise retrieval, pack reuse, and mobile re-entry will get muddy fast.
- sample_inputs:
  - `ily/07-hermes-memory-code-grounded-hidden-logic.md`
  - `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md`
  - `ily/11-purr-session-scope-and-episode-lineage-contract.md`
  - `notes/boards/hermes-memory-review.md`
  - `notes/boards/purr-alignment-brief.md`
- input_format: repo docs + latest Hermes scope/lineage findings
- output_format: cycle-log note covering `owner/purr scoping`, `session_window vs episode`, `resume/reentry continuation policy`, `exact-hit retrieval vs lineage recap`, `pack artifact ownership`
- testable_acceptance: must explicitly reject platform-global or title-based scope, must define `session_window` and `episode` separately, and must explain why retrieval should preserve exact hit evidence before lineage summaries.
- status: queued
- owner: code-worker
- pick order: 8

### phase-one-build-order
- mission: M4 (implementation plan, not implementation yet)
- why: after research we need a clean sequence, not random building.
- sample_inputs:
  - Hermes review
  - Purr alignment brief
  - tool/mobile note
  - Catnet/market note
  - prediction/timing note
  - lifecycle/feedback state-machine note
  - retrieval/context-packer note
  - session-scope/lineage contract note
  - parked build candidates below
- input_format: existing repo docs and parked tasks
- output_format: ordered plan in cycle log naming the first 3 implementation slices and why
- testable_acceptance: must choose a first implementation slice and justify why it beats the others. must keep flashy/social features behind core memory work.
- status: queued
- owner: code-worker
- pick order: 9

---

## parked — build after research

### memory-ledger
- mission: later M1 build
- why parked: good candidate for first build slice after research lock
- status: parked

### memory-candidate-extractor
- mission: later M1/M3 build
- why parked: depends on final memory model and feedback rules
- status: parked

### memory-context-packer
- mission: later M2 build
- why parked: depends on agreed retrieval budget + ranking logic
- status: parked

### feedback-orchestrator
- mission: later M3 build
- why parked: depends on agreed clarification policy
- status: parked

### memory-review-queue
- mission: later M3/M2 build
- why parked: depends on final state model and anti-spam review rules
- status: parked

### social-memory-graph
- mission: future catnet work
- why parked: not before single-purr memory works
- status: parked

### multimodal-memory-ingest
- mission: future
- why parked: text loop first
- status: parked

### purr-world-sim
- mission: future social simulation
- why parked: city comes after memory spine
- status: parked
