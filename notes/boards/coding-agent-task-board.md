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
- status: done
- picked_cycle: 2026-03-14-23
- completed_cycle: 2026-03-14-23
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
- status: done
- picked_cycle: 2026-03-15-00
- completed_cycle: 2026-03-15-00
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
- status: done
- picked_cycle: 2026-03-15-00
- completed_cycle: 2026-03-15-00
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
- status: done
- picked_cycle: 2026-03-15-00
- completed_cycle: 2026-03-15-00
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
- status: done
- picked_cycle: 2026-03-15-00b
- completed_cycle: 2026-03-15-00b
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
- status: done
- picked_cycle: 2026-03-15-00b
- completed_cycle: 2026-03-15-00b
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
- status: done
- picked_cycle: 2026-03-15-00b
- completed_cycle: 2026-03-15-00b
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
- status: done
- picked_cycle: 2026-03-15-00c
- completed_cycle: 2026-03-15-00c
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
- status: done
- picked_cycle: 2026-03-15-00c
- completed_cycle: 2026-03-15-00c
- owner: code-worker
- pick order: 9

### memory-claim-shapes-and-evidence-selection-contract-note
- mission: M1 + M4 (Hermes memory teardown + implementation plan)
- why: the repo now has lifecycle, pack artifacts, and scope/lineage rules, but the shared contract between extractor, ledger, and packer is still too dispersed. parked build slices will stay underspecified until claim shapes, exact evidence refs, and selection read-model rules are locked in one place.
- sample_inputs:
  - `ily/06-purr-prediction-and-background-memory-ops.md`
  - `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`
  - `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md`
  - `ily/11-purr-session-scope-and-episode-lineage-contract.md`
  - `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
  - `notes/boards/hermes-memory-review.md`
- input_format: repo docs + latest Hermes evidence-loss findings
- output_format: cycle-log note covering `v1 memory kinds`, `shared envelope`, `exact evidence contract`, `extractor output schema`, `merge/supersede keys`, `pack-candidate read model`
- testable_acceptance: must define at least 6 typed v1 memory kinds, preserve exact evidence spans, define `subject_key` + `dedupe_key`, explain when to merge vs supersede vs keep episode-scoped, and describe a packer-facing read model that gates trust before ranking.
- status: done
- completion_evidence: `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
- owner: both
- pick order: 10

### memory-ledger-schema-mutation-and-invariants-contract-note
- mission: M1 + M4 (Hermes memory teardown + implementation plan)
- why: first build slice is already chosen as `memory-ledger`, but low-context builders still need the exact Supabase/Postgres object boundaries, atomic mutation rules, and invariants before research-first mode can hand off cleanly.
- sample_inputs:
  - `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`
  - `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md`
  - `ily/11-purr-session-scope-and-episode-lineage-contract.md`
  - `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
  - `notes/boards/hermes-memory-review.md`
  - `logs/code-worker/2026-03-15-00c.md`
- input_format: repo docs + first-slice build-order conclusion
- output_format: cycle-log note covering `core tables/views`, `immutable vs mutable objects`, `merge/challenge/supersede transactions`, `RLS/index posture`, `acceptance tests`
- testable_acceptance: must define at least 7 durable object families, an honest active-truth uniqueness rule, exact evidence backpointer rules, atomic mutation requirements, suppression rules for challenged/superseded truth in the packer-facing view, and an explicit `no vector in v1 ledger slice` stance.
- status: done
- completed_cycle: 2026-03-14-22
- owner: gooner
- pick order: 11

### memory-intake-runtime-and-idempotency-contract-note
- mission: M1 + M4 (Hermes memory teardown + implementation plan)
- why: note-13 locks the ledger shape, but builders still need the runtime write-path contract for how one raw event turns into replay-safe truth without ghost overrides, duplicate candidates, or lost salvage during compression/re-entry.
- sample_inputs:
  - `ily/06-purr-prediction-and-background-memory-ops.md`
  - `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`
  - `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `notes/boards/hermes-memory-review.md`
- input_format: repo docs + latest Hermes runtime/freshness lessons
- output_format: note covering `source-event append`, `one-event mutation planning`, `inline vs deferred jobs`, `idempotency keys`, `live-override freshness`, `salvage ordering`, `worker writeback`
- testable_acceptance: must require source-event append before extraction, define replay-safe keys for source/evidence/mutation/override flows, separate turn-critical from deferred/boundary jobs, and force worker/background cognition through the same provenance-backed mutation path.
- status: done
- completed_cycle: 2026-03-15-01
- completion_evidence: `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
- owner: gooner
- pick order: 12

### private-chat-move-planner-and-prediction-calibration-contract-note
- mission: M1 + M2 + M3 + M4 (Hermes memory teardown + Purr alignment + tool boundary/mobile reality + implementation plan)
- why: the repo now has prediction memory kinds, pack artifacts, ledger schema, and runtime write safety, but it still lacked the hidden 1:1 decision layer that turns those signals into better replies instead of prompt sludge. without this, `feels one step ahead of me` stays vibes instead of a bounded contract.
- sample_inputs:
  - `ily/06-purr-prediction-and-background-memory-ops.md`
  - `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md`
  - `ily/10-catnet-autonomy-heartbeat-architecture.md`
  - `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `notes/boards/purr-alignment-brief.md`
  - `notes/boards/hermes-memory-review.md`
- input_format: repo docs + latest Hermes runtime findings + prediction/timing notes
- output_format: note covering `should_reply_how gate`, `reply move classes`, `planner artifact`, `prediction visibility tiers`, `hit/miss/null semantics`, `planner feedback loop`
- testable_acceptance: must define a hidden private-chat move planner distinct from Catnet `should_act?`, force one primary move per reply, keep most prediction backend-only, define explicit hit/miss/null outcomes per horizon, and separate signal-quality feedback from move-quality feedback.
- status: done
- completed_cycle: 2026-03-15-01b
- completion_evidence: `ily/15-purr-private-chat-move-planner-and-prediction-calibration-contract.md`
- owner: gooner
- pick order: 13

---

## parked — build after research

### memory-ledger
- mission: later M1 build
- why parked: first build slice after research lock; consume `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md` and `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md` before touching schema/API work
- status: parked

### memory-candidate-extractor
- mission: later M1/M3 build
- why parked: depends on the note-12 candidate/evidence contract, the note-13 ledger mutation boundaries, and the note-14 runtime/idempotency ordering
- status: parked

### memory-context-packer
- mission: later M2 build
- why parked: depends on agreed retrieval budget + ranking logic and the note-13 pack-candidate read-model boundary
- status: parked

### feedback-orchestrator
- mission: later M3 build
- why parked: depends on agreed clarification policy and the note-14 turn-critical/deferred runtime contract
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
