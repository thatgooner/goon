# coding-agent task board

MISSION CHANGE — READ THIS FIRST:
- old moltbook/poly lane is archived under `archive/2026-03-14-moltbook-poly-pivot/`
- active mission is now `purr` memory infrastructure
- CURRENT PHASE = research first, build later
- transition state right now = research complete enough for slice 1, but build gate still closed
- if you are code-worker, do not start shipping new tools until the shared boards explicitly unpark `memory-ledger`
- handoff specs / build plans are not authorization by themselves
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

### session-epoch-prompt-artifacts-and-trust-boundary-contract-note
- mission: M1 + M3 + M4 (Hermes memory teardown + tool boundary/mobile reality + implementation plan)
- why: latest Hermes teardown made one seam impossible to ignore — the repo still needed an explicit contract for what the model actually reads, what counts as maintenance-only state, and how compaction/re-entry handoff stays honest. without this, pack reuse can drift, synthetic maintenance artifacts can contaminate recall, and continuation pointers can split across stores.
- sample_inputs:
  - `ily/07-hermes-memory-code-grounded-hidden-logic.md`
  - `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md`
  - `ily/11-purr-session-scope-and-episode-lineage-contract.md`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `ily/15-purr-private-chat-move-planner-and-prediction-calibration-contract.md`
  - `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`
  - `notes/boards/hermes-memory-review.md`
- input_format: repo docs + latest Hermes artifact-hygiene findings
- output_format: cycle-log note covering `artifact planes`, `reuse vs patch vs rebuild`, `typed maintenance artifacts`, `exact-hit recall`, `atomic continuation handoff`, `prompt-material trust gates`
- testable_acceptance: must separate immutable session snapshot from turn overlay; must forbid fake user/Purr maintenance records; must require exact-hit evidence before lineage recap; must forbid compaction-without-preservation; and must define one canonical active leaf for append/resume/re-entry.
- status: done
- completed_cycle: 2026-03-15-03
- completion_evidence: `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`
- owner: both
- pick order: 14

### hermes-memory-failure-matrix-prompt-recall-and-sinks-note
- mission: M1 (Hermes memory teardown)
- why: latest code pass made the cross-lane problem explicit — Hermes is strongest when prompt state is frozen as an artifact, but weaker where prompt-bound sinks, recall evidence, compression survival artifacts, and runtime scope rules do not share one trust/evidence contract. code-worker needs this map so future build work does not copy the seams by accident.
- sample_inputs:
  - `vendor/hermes-agent/run_agent.py`
  - `vendor/hermes-agent/agent/context_compressor.py`
  - `vendor/hermes-agent/tools/memory_tool.py`
  - `vendor/hermes-agent/hermes_state.py`
  - `vendor/hermes-agent/tools/session_search_tool.py`
  - `vendor/hermes-agent/agent/prompt_builder.py`
  - `vendor/hermes-agent/gateway/session.py`
  - `vendor/hermes-agent/gateway/run.py`
  - `ily/05-hermes-memory-behavioral-teardown.md`
  - `ily/07-hermes-memory-code-grounded-hidden-logic.md`
  - `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`
- input_format: repo docs + direct Hermes code inspection
- output_format: note covering `prompt artifact lane`, `live memory sink lane`, `recall/search lane`, `compression/survival lane`, `scope lane`, plus a `steal vs reject` split
- testable_acceptance: must explicitly separate snapshotted prompt material from API-only prompt additions; must call out summary-only recall + child-hit/root-collapse risk; must call out summary-failure truth loss and synthetic transcript artifacts; must call out sink-parity trust gaps; and must translate all of that into Purr rules instead of just criticism.
- status: done
- completed_cycle: 2026-03-15-03
- completion_evidence: `ily/17-hermes-memory-failure-matrix-prompt-recall-and-sinks.md`
- owner: gooner
- pick order: 15

### hidden-cognition-runtime-and-background-job-graph-note
- mission: M1 + M3 + M4 (Hermes memory teardown + tool boundary/mobile reality + implementation plan)
- why: latest Hermes trigger-map pass plus the newer Purr contracts still left one missing handoff for builders — which invisible jobs are truly turn-critical, which are boundary-critical, which are deferred maintenance, and which belong in proactive heartbeat only. without this split, people will either rebuild too much on the hot path or smuggle memory tooling into visible chat theater.
- sample_inputs:
  - `vendor/hermes-agent/run_agent.py`
  - `vendor/hermes-agent/gateway/run.py`
  - `vendor/hermes-agent/gateway/session.py`
  - `vendor/hermes-agent/tools/session_search_tool.py`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `ily/15-purr-private-chat-move-planner-and-prediction-calibration-contract.md`
  - `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`
  - `ily/17-hermes-memory-failure-matrix-prompt-recall-and-sinks.md`
- input_format: Hermes trigger/control findings + latest Purr runtime contracts
- output_format: note covering `turn-critical lane`, `boundary-critical lane`, `deferred maintenance lane`, `proactive heartbeat lane`, and `internal tool boundary`
- testable_acceptance: must explicitly require source-event append before hot-path extraction, keep same-turn freshness in a tiny committed overlay instead of full rebuild, define salvage/handoff ordering for compaction or mobile re-entry, set stricter rules for proactive jobs than normal replies, and keep these jobs backend-only rather than user-facing tool ceremony.
- status: done
- completed_cycle: 2026-03-15-04
- completion_evidence: `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
- owner: gooner
- pick order: 16

### pattern-rollups-proactive-preflight-and-cost-tier-contract-note
- mission: M1 + M3 + M4 (Hermes memory teardown + tool boundary/mobile reality + implementation plan)
- why: the repo already had predictive memory kinds, reply-time planning, pack budgets, and heartbeat lanes, but it still lacked the cheap/private read-model between raw prediction memory and actual texting-first behavior. without this note, builders can still either rescan too much ledger state per wakeup or let vague pattern vibes drive creepy/spammy pings.
- sample_inputs:
  - `ily/06-purr-prediction-and-background-memory-ops.md`
  - `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md`
  - `ily/10-catnet-autonomy-heartbeat-architecture.md`
  - `ily/15-purr-private-chat-move-planner-and-prediction-calibration-contract.md`
  - `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
  - `notes/boards/hermes-memory-review.md`
  - `notes/boards/purr-alignment-brief.md`
- input_format: repo docs + latest Hermes timing/discipline lessons
- output_format: note covering `derived proactive artifacts`, `pattern/timing/posture rollups`, `should_text_first? gate`, `proactive_pack slots`, `cooldowns/budgets`, and `cost-tier degradation`
- testable_acceptance: must define at least 4 proactive-facing derived artifacts, force heartbeat to read derived state instead of raw ledger fanout, define hard vetoes + smallest valid move order for texting-first decisions, lock concrete `proactive_pack` slot caps, and explicitly cut proactive frequency/model arbitration before weakening memory integrity.
- status: done
- completed_cycle: 2026-03-15-06
- completion_evidence: `ily/19-purr-pattern-rollups-proactive-preflight-and-cost-tier-contract.md`
- owner: gooner
- pick order: 17

### feedback-orchestrator-review-outcomes-and-trust-decay-contract-note
- mission: M1 + M3 + M4 (Hermes memory teardown + tool boundary/mobile reality + implementation plan)
- why: the repo now has lifecycle, queue fields, runtime lanes, and proactive review pings, but the missing product-grade seam was still how memory verification actually gets selected, interpreted, and written back. without this note, builders can still turn review into needy admin sludge or let stale truth rot because silence/contradiction/passive reconfirmation are not separated cleanly.
- sample_inputs:
  - `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
  - `ily/19-purr-pattern-rollups-proactive-preflight-and-cost-tier-contract.md`
  - `notes/boards/hermes-memory-review.md`
  - `notes/boards/purr-alignment-brief.md`
- input_format: repo docs + latest Hermes review/decay gap findings
- output_format: note covering `feedback surfaces`, `review queue vs truth-state split`, `explicit/passive outcome taxonomy`, `no_signal semantics`, `trust-decay propagation`, and `proactive review gating`
- testable_acceptance: must define at least 5 feedback surfaces, explicitly separate `confirmed_explicit` / `confirmed_passive` / `contradicted_explicit` / `contradicted_passive` / `no_signal` / `not_now`, state that silence is usually `no_signal` rather than contradiction, split `memory_item.review_status` from queue-item execution status, and explain how review outcomes propagate into pack policy plus proactive artifacts.
- status: done
- completed_cycle: 2026-03-15-07
- completion_evidence: `ily/20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md`
- owner: gooner
- pick order: 18

### hermes-dogfood-memory-judge-and-integration-eval
- mission: M4 pre-build validation / dogfood strategy
- why: before committing the Purr memory spine directly into the product, we want one pressure-test on two open strategic questions: should ambiguous memory updates use a narrower reasoning/judge layer on top of the deterministic ledger pipeline, and should the first live dogfood happen inside Hermes (where Ilyas is already talking on Telegram) before direct Purr integration.
- sample_inputs:
  - `ily/21-purr-research-consolidated-state-and-build-handoff.md`
  - `ily/22-hermes-dogfood-memory-backend-evaluation.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `ily/15-purr-private-chat-move-planner-and-prediction-calibration-contract.md`
  - `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
  - `ily/20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md`
  - `vendor/hermes-agent/run_agent.py`
  - `vendor/hermes-agent/hermes_state.py`
  - `vendor/hermes-agent/tools/memory_tool.py`
  - `vendor/hermes-agent/tools/session_search_tool.py`
- input_format: existing Purr memory contracts + Hermes memory runtime surface + explicit user context that Ilyas is actively talking to Hermes on Telegram now
- output_format: cycle-log note covering `deterministic backbone vs judge layer`, `where agentic judgment can/cannot sit`, `Hermes-first dogfood verdict`, `phased rollout inside Hermes`, `instrumentation/debug posture`, `success signals`, and `kill signals`
- testable_acceptance: must explicitly keep source-event append / evidence refs / mutation transactions / hard pack budgets deterministic; must give a direct yes/no/partial on Hermes-first dogfood; if yes, must define at least 4 phases (shadow ledger, read-only pack compare, correction override, later review/proactive); must clearly say Hermes dogfood is backend-memory validation, not "turn Hermes into Purr"; must state whether this changes build order or only test order.
- status: done
- picked_cycle: 2026-03-15-18
- completed_cycle: 2026-03-15-18
- completion_evidence: `ily/23-hermes-dogfood-judge-layer-and-integration-verdict.md`
- owner: code-worker
- pick order: 19

### referee-layer-vs-narrow-evaluator-followup
- mission: M4 pre-build validation / dogfood strategy follow-up
- why: ily/23 correctly rejected subagents inside the memory loop and preferred a narrow typed evaluator. but there is still one higher-level question worth pressure-testing before implementation planning: whether a slower referee/audit layer above the deterministic system could add value for quality-control on churny or suspicious memory clusters without contaminating the truth spine.
- sample_inputs:
  - `ily/23-hermes-dogfood-judge-layer-and-integration-verdict.md`
  - `ily/24-referee-layer-vs-narrow-evaluator-followup.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
  - `ily/20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md`
  - `vendor/hermes-agent/run_agent.py`
  - `vendor/hermes-agent/hermes_state.py`
- input_format: prior judge-layer verdict + explicit follow-up question about a slower higher-level referee layer sitting above, not inside, the deterministic memory pipeline
- output_format: cycle-log note covering `is referee layer useful`, `offline auditor vs escalation path vs repair worker`, `what it must never do`, `what should trigger it`, `runtime form`, `does it help Hermes dogfood`, and `build-order impact`
- testable_acceptance: must give a direct yes/no/partial; must explicitly preserve deterministic ownership of source-event append / evidence refs / mutation contracts / hard budgets; must compare no-referee vs offline auditor vs escalation path vs repair worker; must say whether a true subagent is useful or overkill here; must clearly state whether this should exist before dogfood, during dogfood, or only much later.
- status: done
- picked_cycle: 2026-03-15-19
- completed_cycle: 2026-03-15-19
- completion_evidence: `ily/25-memory-health-auditor-verdict.md`
- owner: code-worker
- pick order: 20

### hermes-shadow-dogfood-adapter-and-tap-boundary-contract-note
- mission: M1 + M4 pre-build validation / dogfood strategy
- why: ily/23 approved Hermes-first dogfood as a shadow-only backend validation path, but the repo still lacked the code-grounded contract for where to tap Hermes safely, what data Hermes actually preserves, and how to avoid entangling the adapter with Hermes behavior or muddy routing/provenance during resets and compression.
- sample_inputs:
  - `vendor/hermes-agent/gateway/hooks.py`
  - `vendor/hermes-agent/gateway/session.py`
  - `vendor/hermes-agent/gateway/run.py`
  - `vendor/hermes-agent/hermes_state.py`
  - `vendor/hermes-agent/gateway/platforms/base.py`
  - `vendor/hermes-agent/gateway/platforms/telegram.py`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`
  - `ily/23-hermes-dogfood-judge-layer-and-integration-verdict.md`
  - `ily/25-memory-health-auditor-verdict.md`
- input_format: direct Hermes code inspection + existing Purr dogfood/runtime contracts
- output_format: note covering `best tap points`, `what Hermes preserves vs loses`, `phase 0-2 adapter responsibilities`, `bridge/invariants`, `failure modes`, and `kill signals`
- testable_acceptance: must explicitly prefer hook-triggered read-only snapshots from `state.db` over an embedded adapter; must call out that SQLite lacks durable chat/thread/provider-message ids; must reject naive row-tail ingestion because resets/compression can rewrite or fork transcript continuity; and must require a separate Purr-owned historical session-origin bridge instead of trusting Hermes `session_key` or current `sessions.json` as durable identity.
- status: done
- completed_cycle: 2026-03-15-08
- completion_evidence: `ily/26-hermes-shadow-dogfood-adapter-and-tap-boundary-contract.md`
- owner: gooner
- pick order: 21

### build-mode-entry-gates-and-slice-acceptance-matrix-note
- mission: M4 (implementation plan, not implementation yet)
- why: the repo had enough research to build from, but low-context agents could still misread handoff docs and dogfood plans as permission to start building. we needed one explicit transition contract that says what is truly locked, what still gates unpark, and what each early slice may or may not ship.
- sample_inputs:
  - `ily/21-purr-research-consolidated-state-and-build-handoff.md`
  - `ily/23-hermes-dogfood-judge-layer-and-integration-verdict.md`
  - `ily/25-memory-health-auditor-verdict.md`
  - `ily/26-hermes-shadow-dogfood-adapter-and-tap-boundary-contract.md`
  - `ily/26-hermes-dogfood-implementation-plan-summary.md`
  - `notes/boards/weekly-missions.md`
  - `notes/boards/coding-agent-task-board.md`
- input_format: repo handoff docs + board state + dogfood/build-order notes
- output_format: note covering `current transition state`, `research-lock exit gates`, `main slice order`, `slice acceptance matrix`, and `dogfood attachment rules`
- testable_acceptance: must explicitly state `research complete, build gate closed`; must require board-level unpark before any implementation starts; must keep dogfood as validation-track-only; and must define what slices 1-4 must/must-not ship so low-context builders do not drift.
- status: done
- completed_cycle: 2026-03-15-09
- completion_evidence: `ily/27-purr-build-mode-entry-gates-and-slice-acceptance-matrix.md`
- owner: gooner
- pick order: 22

### hermes-shadow-dogfood-scorecard-and-observability-contract-note
- mission: M1 + M4 pre-build validation / dogfood strategy
- why: ily/23 approved shadow dogfood and ily/26 locked the tap boundary, but the repo still lacked the honest evaluation contract for what Hermes actually lets us measure, what is only a lossy baseline, and what counts as real validation instead of plumbing vibes.
- sample_inputs:
  - `vendor/hermes-agent/gateway/run.py`
  - `vendor/hermes-agent/gateway/session.py`
  - `vendor/hermes-agent/hermes_state.py`
  - `vendor/hermes-agent/run_agent.py`
  - `ily/23-hermes-dogfood-judge-layer-and-integration-verdict.md`
  - `ily/26-hermes-shadow-dogfood-adapter-and-tap-boundary-contract.md`
  - `ily/27-purr-build-mode-entry-gates-and-slice-acceptance-matrix.md`
- input_format: direct Hermes code inspection + existing dogfood/runtime contracts
- output_format: note covering `observable surfaces`, `lossy/blind surfaces`, `shadow-dogfood scorecard`, `pass/fail verdict logic`, and `kill signals`
- testable_acceptance: must explicitly state that stored `sessions.system_prompt` is only a baseline compare surface rather than guaranteed full provider-facing prompt on gateway turns; must separate reliable observability bundle vs fake-confidence surfaces; must define concrete score dimensions for ingestion fidelity, correction freshness, pack quality, recall evidence quality, and review/proactive safety; and must say what outputs are allowed (`validated_plumbing`, `useful_plumbing_signal`, `insufficient_data`, `failed_boundary`).
- status: done
- completed_cycle: 2026-03-15-10
- completion_evidence: `ily/28-hermes-shadow-dogfood-scorecard-and-observability-contract.md`
- owner: gooner
- pick order: 23

### memory-intake-extractor-routing-and-evaluator-trigger-contract-note
- mission: M1 + M4 (Hermes memory teardown + implementation plan)
- why: the repo had already locked runtime ordering, typed claim shapes, and the narrow evaluator verdict, but the actual `memory-candidate-extractor` lane still had one open seam: whether intake should stay rules-only, use a cheap structured model, or blur into a second reasoning brain. low-context builders needed one explicit routing contract before slice 2 eventually opens.
- sample_inputs:
  - `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `ily/23-hermes-dogfood-judge-layer-and-integration-verdict.md`
  - `ily/25-memory-health-auditor-verdict.md`
  - `ily/27-purr-build-mode-entry-gates-and-slice-acceptance-matrix.md`
  - `ily/28-hermes-shadow-dogfood-scorecard-and-observability-contract.md`
- input_format: existing Purr runtime/evaluator contracts + latest build-gate discipline
- output_format: note covering `deterministic prefilters`, `inline vs deferred extractor`, `extractor vs evaluator ownership`, `routing matrix`, `cost-tier degradation order`, and `slice-2 acceptance posture`
- testable_acceptance: must give a direct answer on `rule-only vs cheap-model vs hybrid`; must keep truth commits deterministic; must reserve evaluator usage for the already-approved narrow ambiguity points; must explicitly forbid turning the main reply model into the normal intake truth engine; and must keep the auditor out of the hot loop.
- status: done
- completed_cycle: 2026-03-15-11
- completion_evidence: `ily/29-purr-memory-intake-extractor-routing-and-evaluator-trigger-contract.md`
- owner: gooner
- pick order: 24

### supabase-local-dev-operational-gate-clarification-note
- mission: M4 (implementation plan, not implementation yet)
- why: the repo had already identified Supabase setup as the only honest blocker before build, but the actual local-dev path lived inside parked dogfood docs, which made it too easy for low-context builders to confuse `setup exists` with `build is authorized` or to shrink slice 1 down to dogfood phase-0 scope.
- sample_inputs:
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/21-purr-research-consolidated-state-and-build-handoff.md`
  - `ily/27-purr-build-mode-entry-gates-and-slice-acceptance-matrix.md`
  - `ily/29-purr-memory-intake-extractor-routing-and-evaluator-trigger-contract.md`
  - `tools/hermes-dogfood-adapter/README.md`
  - `docs/plans/2026-03-15-hermes-purr-memory-dogfood-implementation-plan.md`
- input_format: build-gate docs + existing Supabase setup references already present in repo
- output_format: note covering `local-first Supabase stance`, `repo-root vs tool-local canonical home`, `default migration runner posture`, `env/write-security stance`, `dogfood-vs-mainline scope boundary`, and `authorization rule`
- testable_acceptance: must explicitly prefer local Supabase CLI before hosted deployment; must keep build authorization board-gated; must state that dogfood phase-0 schema is not the full `memory-ledger` slice; must preserve backend/service-role write posture; and must name repo root as the future canonical home for mainline Supabase scaffold/migrations.
- status: done
- completed_cycle: 2026-03-15-13
- completion_evidence: `ily/30-purr-supabase-local-dev-operational-gate-clarification.md`
- owner: gooner
- pick order: 25

### memory-golden-scenarios-and-eval-fixture-contract-note
- mission: M1 + M4 (Hermes memory teardown + implementation plan / pre-build validation)
- why: the repo already had slice acceptance prose and a Hermes shadow-dogfood scorecard, but it still lacked one frozen set of seam-focused golden scenarios tying together ledger, runtime, packer, feedback, and proactive restraint. without this, future builders could ship migrations/tests that pass locally while still missing the exact Hermes-derived failures we care about.
- sample_inputs:
  - `ily/21-purr-research-consolidated-state-and-build-handoff.md`
  - `ily/28-hermes-shadow-dogfood-scorecard-and-observability-contract.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
  - `ily/20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md`
  - `notes/boards/hermes-memory-review.md`
- input_format: existing Purr contracts + Hermes failure findings + current dogfood score dimensions
- output_format: note covering `canonical golden scenarios`, `minimum adversarial fixture bundles`, `slice mapping`, `scorecard mapping`, and `what this closes vs what remains build-time`
- testable_acceptance: must define at least 8 seam-focused golden scenarios; must include correction freshness, owner isolation, contradiction suppression, salvage-before-close, exact evidence vs summary, and silence!=contradiction; must map scenarios to both early build slices and Hermes shadow-dogfood score dimensions; and must explicitly say this closes the eval contract, not the runnable fixture/harness work.
- status: done
- completed_cycle: 2026-03-15-14
- completion_evidence: `ily/31-purr-memory-golden-scenarios-and-eval-fixture-contract.md`
- owner: gooner
- pick order: 26

### owner-auth-and-origin-binding-contract-note
- mission: M2 + M3 + M4 (Purr alignment + tool/mobile reality + implementation plan)
- why: the internal memory spine was already locked, but the repo still had one implied seam at the front door: how World/mobile auth, notification re-entry, proactive wakeups, and Hermes shadow origins bind into the right `owner_id`, `purr_id`, and active continuity leaf without turning convenience ids into product identity. low-context builders could otherwise confuse `owner_surface`, `entry_surface`, and live routing metadata.
- sample_inputs:
  - `ily/11-purr-session-scope-and-episode-lineage-contract.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`
  - `ily/26-hermes-shadow-dogfood-adapter-and-tap-boundary-contract.md`
  - `ily/27-purr-build-mode-entry-gates-and-slice-acceptance-matrix.md`
  - `ily/28-hermes-shadow-dogfood-scorecard-and-observability-contract.md`
  - `notes/boards/purr-alignment-brief.md`
- input_format: existing Purr scope/lineage contracts + Hermes shadow-origin findings + current build-gate rules
- output_format: note covering `auth_principal -> owner/purr binding`, `origin_channel vs surface_family`, `server-owned binding rules`, `continuation/re-entry matrix`, `shadow-vs-mainline separation`, and `build-order impact`
- testable_acceptance: must give a direct answer on whether this blocks slice 1; must freeze the meaning of `owner_surface`; must define `owner_auth_binding` and `origin_bridge`; must require server-owned active-leaf resolution; must state that app-open alone is not a conversation event; and must explicitly reject raw webview session ids or Hermes `session_key` as durable identity truth.
- status: done
- completed_cycle: 2026-03-15-15
- completion_evidence: `ily/32-purr-owner-auth-and-origin-binding-contract.md`
- owner: gooner
- pick order: 27

### hermes-memory-runtime-quality-boosters-note
- mission: M1 (Hermes memory teardown)
- why: prior teardown notes locked truth-shape, scope, evidence, and boundary failures, but still under-explained why Hermes often *feels* sharper than its flat memory deserves. low-context builders could otherwise copy the wrong lesson — either `flat memory is enough` or `runtime choreography does not matter`.
- sample_inputs:
  - `vendor/hermes-agent/run_agent.py`
  - `vendor/hermes-agent/hermes_state.py`
  - `vendor/hermes-agent/agent/context_compressor.py`
  - `vendor/hermes-agent/gateway/run.py`
  - `vendor/hermes-agent/gateway/session.py`
  - `ily/17-hermes-memory-failure-matrix-prompt-recall-and-sinks.md`
  - `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
- input_format: direct Hermes runtime code + existing teardown notes
- output_format: note covering `next-turn recall prefetch`, `continuation repair`, `working-state survival across compression`, `prompt-vs-transcript plane separation`, `boundary-critical background hygiene`, and `resume-by-artifact behavior`
- testable_acceptance: must explicitly explain why these tricks improve perceived memory without fixing Hermes' flat truth model; must separate what Purr should steal vs reject; and must state that this sharpens runtime quality requirements without changing slice order.
- status: done
- completed_cycle: 2026-03-15-16
- completion_evidence: `ily/33-hermes-memory-runtime-quality-boosters-prefetch-repair-and-artifact-separation.md`
- owner: gooner
- pick order: 28

### private-reply-move-outcome-writeback-and-goldens-note
- mission: M1 + M4 (Hermes memory teardown + implementation plan / eval discipline)
- why: `ily/15` locks the hidden private-chat move planner, but the actual durable writeback contract for reply-time prediction/move outcomes is still too implied. `ily/31` also freezes golden scenarios for ledger/runtime/feedback/proactive seams without yet covering private reply-planner outcome seams directly. this is the cleanest remaining research gap around `feels one step ahead` without prompt bloat.
- sample_inputs:
  - `ily/15-purr-private-chat-move-planner-and-prediction-calibration-contract.md`
  - `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
  - `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
  - `ily/19-purr-pattern-rollups-proactive-preflight-and-cost-tier-contract.md`
  - `ily/20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md`
  - `ily/31-purr-memory-golden-scenarios-and-eval-fixture-contract.md`
- input_format: existing planner/runtime/eval notes
- output_format: note covering `reply-time outcome artifacts`, `signal vs move vs pack outcome split`, `horizon-closure ownership`, `writeback semantics for response_value/timing_value`, and `private reply-planner golden scenarios`
- testable_acceptance: must explicitly freeze whether reply-time calibration lives in `memory_events`, typed maintenance artifacts, or a hybrid; must preserve separate `prediction_outcome`, `move_outcome`, and `pack_outcome` planes; must define at least 5 private reply-planner goldens; and must keep the whole seam backend-only rather than prompt-visible theater.
- status: done
- completed_cycle: 2026-03-15-18c
- completion_evidence: `ily/34-purr-private-reply-move-outcome-writeback-and-goldens.md`
- owner: gooner
- pick order: 29

### reply-repair-boundary-and-outcome-hygiene-note
- mission: M1 + M4 (Hermes memory teardown + implementation plan / eval discipline)
- why: `ily/33` makes one thing obvious right after note 34: Hermes gets real continuity mileage from continuation repair, truncation recovery, and artifact-level handoff, but none of that automatically tells us how repaired/partial/private-chat turns should count in outcome calibration. without one explicit contract here, future builders can accidentally count repaired or synthetic control text as real move success, or let transcript rewrite/compression muddy reply-eval evidence.
- sample_inputs:
  - `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`
  - `ily/18-purr-hidden-cognition-runtime-and-background-job-graph.md`
  - `ily/33-hermes-memory-runtime-quality-boosters-prefetch-repair-and-artifact-separation.md`
  - `ily/34-purr-private-reply-move-outcome-writeback-and-goldens.md`
  - `vendor/hermes-agent/run_agent.py`
  - `vendor/hermes-agent/agent/context_compressor.py`
  - `vendor/hermes-agent/hermes_state.py`
- input_format: latest Purr runtime/eval notes + Hermes repair/compression code
- output_format: note covering `repair artifact plane`, `partial turn states`, `move-outcome closure under truncation/retry`, `repair vs transcript truth`, and `repair-focused goldens`
- testable_acceptance: must explicitly separate `repair_outcome` from `move_outcome`; must forbid synthetic repair/control text from counting as raw chat evidence or prompt-selection proof; must define how truncated/continued turns stay attached to one `plan_id`; and must give at least 4 goldens around truncation, retry, rollback, and compression handoff.
- status: queued
- owner: gooner
- pick order: 30

---

## parked — build after research

### memory-ledger
- mission: later M1 build
- why parked: first build slice after research lock; consume `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`, `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`, and `ily/30-purr-supabase-local-dev-operational-gate-clarification.md` before touching schema/API work
- clarification: do **not** treat `tools/hermes-dogfood-adapter/` setup/migrations as build authorization or as the full slice-1 scope.
- status: parked

### memory-candidate-extractor
- mission: later M1/M3 build
- why parked: depends on the note-12 candidate/evidence contract, the note-13 ledger mutation boundaries, the note-14 runtime/idempotency ordering, and the note-29 intake-routing contract that freezes `rules vs cheap structured extractor vs narrow evaluator` boundaries before slice 2 opens
- status: parked

### memory-context-packer
- mission: later M2 build
- why parked: depends on agreed retrieval budget + ranking logic and the note-13 pack-candidate read-model boundary
- status: parked

### hermes-shadow-dogfood-adapter-phase-0-2
- mission: later M4 pre-build validation / dogfood
- why parked: depends on `memory-ledger`, `memory-candidate-extractor`, and `memory-context-packer`; consume `ily/23-hermes-dogfood-judge-layer-and-integration-verdict.md` plus `ily/26-hermes-shadow-dogfood-adapter-and-tap-boundary-contract.md`; must stay a hook-triggered, read-only external observer that mirrors Hermes turns into the Purr ledger and runs pack compare without changing Hermes behavior.
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
