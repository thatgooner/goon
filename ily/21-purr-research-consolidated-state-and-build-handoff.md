# Purr research consolidated state + build handoff

## why this note exists
notes 05-20 plus 4 code-worker logs, 5 board files, and the day-1 daily note now contain a complete research body.
but that body is spread across 20+ files with layered depth and no single sync check.

this note does not invent new research.
it consolidates what is already locked, identifies where code-worker and gooner agree or drift, flags real gaps that remain before build, and names the exact handoff for the first implementation slice.

rules for this pass:
- no new lanes
- no vague insights restating what notes 05-20 already locked
- no code
- only synthesis, gap check, and handoff

---

## what is already locked

these contracts are stable across multiple notes and both agents agree on them.
a builder should treat them as input, not open questions.

### 1. identity model
- `1 human = 1 purr` is a data rule, not copy
- `owner_id` + `purr_id` mandatory on every durable row and every retrieval path
- `memory_lane` (`private_1_1 | public_safe | catnet | system_ops`) on every memory object
- cross-user bleed is a product-killing failure, not a footnote
- locked in: notes 11, 12, 13; system-board; purr-alignment-brief

### 2. memory lifecycle states
- core set: `candidate | confirmed | stale | rejected | superseded`
- overlay: `review_status`, `contradiction_status`, `pack_policy`
- transitions are explicit and evented through `memory_events`
- contradictions become state transitions, not text coexistence
- `challenged` truth is suppressed from hot factual pack until resolved
- locked in: notes 08, 12, 13

### 3. evidence contract
- exact spans (`message_id`, `window_id`, `episode_id`, `span_start/end`) are first-class
- summaries are navigation aids only, never canonical truth
- `memory_evidence_refs` are immutable
- summary-derived evidence must backpoint to raw refs
- locked in: notes 12, 13, 16

### 4. ledger schema
- 7 durable object families: identity refs (`owners`, `purrs`), continuity (`episodes`, `session_windows`), raw events (`message_events`), truth rows (`memory_items`), audit trail (`memory_events`), evidence (`memory_evidence_refs`), pack artifacts (`pack_artifacts`)
- `memory_items` is mutable current truth; everything else is append-only
- `pack_candidate_view` is the packer-facing read model
- 10 invariants defined (identity scope, evidence-backed truth, active-truth uniqueness, atomic mutation, etc.)
- no vector in v1 ledger slice
- locked in: note 13

### 5. intake runtime
- source-event append before extraction
- one source event → one coherent mutation plan
- replay-safe idempotency keys for source, evidence, mutation, and override flows
- commit-before-use: the next reply reads committed truth + explicit committed override only
- correction detection outranks generic extraction
- locked in: note 14

### 6. pack artifacts and budget discipline
- 4 pack types: `session_pack`, `turn_delta_pack`, `reentry_pack`, `proactive_pack`
- concrete token budgets (session 500-800/1000, delta 30-120/180, reentry 350-650/800, proactive 120-250/350)
- slot caps per lane (A: boundaries 3, identity 3, preferences 4; B: texture 3, loops 3; C: episodic 2, patterns 2, predictions 0-2; D: evidence 2)
- reuse by default, patch for corrections, rebuild only at real boundaries
- free tier cuts throughput/model/proactive before memory integrity
- locked in: notes 09, 13, 16

### 7. hidden cognition lanes
- 4 invisible runtime lanes: turn-critical, boundary-critical, deferred maintenance, proactive heartbeat
- all lanes share the same scope/evidence/mutation contract
- no visible tool theater
- locked in: notes 06, 18

### 8. private chat move planner
- `should_reply_how?` gate after intake commits, before reply generation
- 7 move classes: direct_reply, direct_reply_plus_callback, direct_reply_plus_preempt, clarify_now, tone_shift, loop_probe, prediction_suppressed
- one primary move per reply, max 1 secondary caution, max 1 pack hint
- prediction visibility tiers: backend-only, planner-visible, compact pack hint, never-visible
- locked in: note 15

### 9. session epoch and prompt artifacts
- 5 typed planes: durable ledger truth, session snapshot artifact, turn overlay artifact, evidence recall artifact, maintenance artifact
- immutable session epoch snapshots
- maintenance artifacts must never masquerade as user/purr speech
- compaction is fork-and-handoff, not in-place rewrite
- atomic continuation pointer handoff
- locked in: note 16

### 10. proactive preflight and cost tiers
- derived predictive artifacts (pattern rollup, timing rollup, posture rollup, preflight summary)
- `should_text_first?` gate with hard vetoes and smallest-valid-move order
- concrete `proactive_pack` slot caps
- cost-tier degradation: cut proactive frequency and model strength before memory integrity
- locked in: note 19

### 11. feedback orchestrator and trust decay
- at least 5 feedback surfaces (inline correction, explicit review prompt, passive behavioral reconfirmation, contradiction detection, no-signal/non-response)
- outcome taxonomy: confirmed_explicit, confirmed_passive, contradicted_explicit, contradicted_passive, no_signal, not_now
- silence is usually `no_signal`, not contradiction
- `review_status` on memory item is separate from queue-item execution status
- review outcomes propagate into pack policy and proactive eligibility
- locked in: note 20

### 12. Hermes steal/reject
- steal: frozen session pack, bounded hot memory, transcript/curated split, pre-compression salvage, stored prompt reuse, structural integrity, security scanning, search→summarize discipline
- reject: flat text truth, substring mutation, same-session stale reads, unscoped recall, title-based pseudo-lineage, chat-loop nudge capture, global namespace, no lifecycle/confidence/review
- locked in: notes 05, 07, 17; hermes-memory-review board

### 13. product voice and anti-patterns
- purr is a persistent alien-cat intelligence, not a chatbot with branding
- memory is the product, not side infra
- no dashboard pet, no visible tool-call theater, no generic wholesome assistant cat
- roasts must be memory-backed, specific, and earned
- catnet is later and must not corrupt private memory core
- locked in: purr-alignment-brief; notes 06, 10

### 14. catnet architecture stance
- server-side wakeup system, not always-on agent swarm
- `should_act?` gate before generation; most wakeups → no-op
- private memory firewall: catnet reads only public-safe abstraction, never raw 1:1 memory
- phased market rollout: social only → system markets → template markets → human-through-purr proposals
- locked in: note 10

### 15. build order
- slice 1: memory-ledger
- slice 2: memory-candidate-extractor
- slice 3: memory-context-packer
- slice 4: feedback-orchestrator
- then: review queue, social graph, multimodal, world sim
- locked in: code-worker log 2026-03-15-00c; task board parked section

---

## where code-worker and gooner agree

| area | gooner position | code-worker position | sync |
|------|----------------|---------------------|------|
| first build slice | memory-ledger | memory-ledger | yes |
| identity model | owner_id + purr_id mandatory | owner_id + purr_id mandatory | yes |
| hermes steal: frozen session pack | steal | steal, independently verified in code | yes |
| hermes reject: flat text truth | reject | reject, independently verified in code | yes |
| hermes reject: stale same-session reads | reject, needs live override | reject, needs live override | yes |
| memory lifecycle states | 5 states + 3 overlays | 5 states + 3 overlays | yes |
| pack artifacts | 4 types with budgets | 4 types with budgets | yes |
| contradiction handling | challenge + suppress + atomic supersede | challenge + suppress + atomic supersede | yes |
| product voice | alien-cat, not dashboard pet | alien-cat, not dashboard pet | yes |
| tools stance | internal only, no visible theater | internal only, no visible theater | yes |
| catnet order | after private memory | after private memory | yes |
| vector in v1 | no | no | yes |
| research-first phase | complete, ready to close | all 9 research tasks done | yes |

verdict: **no meaningful drift detected between code-worker and gooner.**

code-worker's 9 research tasks (logs 2026-03-14-23 through 2026-03-15-00c) independently verified gooner's architecture findings and reached the same conclusions. gooner then extended depth with notes 12-20, which code-worker has not yet independently reviewed line-by-line, but the contracts in those notes are consistent with code-worker's earlier positions.

---

## overlap / duplicate work

| overlap | files | verdict |
|---------|-------|---------|
| Hermes teardown appears 3× | note 05 (behavioral), note 07 (code-grounded), note 17 (failure matrix) | not duplicate — intentional layering. 05 is behavioral, 07 adds code verification, 17 adds cross-lane failure analysis. all 3 are needed. |
| hermes-memory-review.md vs notes 05/07/17 | board file vs ily/ notes | board file is the consolidated summary for quick reference. notes are the depth. keep both. |
| pack contract appears in 5 places | notes 09, 12, 13, 16, 19 | not duplicate — each note adds a different contract layer (budget/slots, selection model, schema, epoch semantics, proactive slots). treat note 09 as the packing-behavior reference and note 13 as the schema reference. |
| code-worker logs repeat findings from ily/ notes | logs vs notes | expected — code-worker was doing independent verification. logs are cycle records, notes are canonical architecture. logs can be treated as historical after this consolidation. |
| memory kinds appear in notes 06, 08, 12 | prediction kinds, lifecycle, claim shapes | layering again. note 12 is the canonical v1 claim-shape contract. notes 06 and 08 are the architectural reasoning that led to it. |

verdict: **no real duplicates. layering is intentional and useful. no cleanup needed.**

---

## real unresolved gaps before build

### gap 1 — no SQL migration file exists
note 13 defines the schema contract in detail. but no actual `.sql` file, Supabase migration, or runnable DDL exists yet. this is the first thing the build slice must produce.

### gap 2 — extractor LLM dependency not specified
note 14 defines the intake runtime contract. notes 06 and 12 define what the extractor should output. but the actual extraction mechanism (cheap model? rule-based first pass? hybrid?) is not locked. the first extractor build will need to decide this.

priority: medium. this blocks slice 2 (extractor), not slice 1 (ledger).

### gap 3 — idempotency key implementation details
note 14 specifies the contract (source-event identity, intake-batch identity, evidence identity, mutation-intent identity, override identity, salvage checkpoints). but the exact Postgres implementation (unique constraints? advisory locks? idempotency table?) is not spelled out.

priority: medium. relevant to slice 1 schema work.

### gap 4 — cost-tier degradation parameters
note 19 defines the policy (cut proactive frequency and model strength before memory integrity). but no concrete parameters exist (e.g., free tier = max N proactive pings/day, model X for extraction, model Y for replies).

priority: low. this is a tuning decision that comes after the core memory spine ships.

### gap 5 — no test fixtures or seed data
the repo has no example memory items, evidence refs, or pack artifacts that a builder could use for local testing. acceptance tests are described in notes 13, 14, 15, 16, 19, 20 but are prose, not runnable.

priority: medium. should be part of the first build slice.

### gap 6 — Supabase project setup not documented
the repo assumes Supabase is the system of record. no project URL, local dev setup, or connection pattern is documented.

priority: high for build start. the first build task should include setup instructions.

---

## which docs are source-of-truth now

### canonical architecture contracts (read these for build)
| doc | role |
|-----|------|
| `ily/08` | memory lifecycle + feedback state machine |
| `ily/09` | retrieval context packer + pack lifecycle |
| `ily/11` | session scope + episode lineage |
| `ily/12` | memory claim shapes + evidence + selection |
| `ily/13` | ledger schema + mutation + invariants (first build-slice spec) |
| `ily/14` | intake runtime + idempotency |
| `ily/15` | private chat move planner + prediction calibration |
| `ily/16` | session epoch + prompt artifacts + trust boundary |
| `ily/18` | hidden cognition runtime + background job graph |
| `ily/19` | pattern rollups + proactive preflight + cost tier |
| `ily/20` | feedback orchestrator + review outcomes + trust decay |

### Hermes reference (read for context, not for build spec)
| doc | role |
|-----|------|
| `ily/05` | behavioral teardown |
| `ily/07` | code-grounded hidden logic |
| `ily/17` | failure matrix + cross-lane alignment |
| `notes/boards/hermes-memory-review.md` | consolidated steal/reject summary |

### product direction (read for taste, not for schema)
| doc | role |
|-----|------|
| `notes/boards/purr-alignment-brief.md` | product voice + constraints |
| `notes/boards/system-board.md` | mission + priorities + routing |
| `notes/boards/weekly-missions.md` | current week missions + status |
| `ily/10` | catnet architecture stance (parked lane) |

### operational (read for process)
| doc | role |
|-----|------|
| `notes/boards/coding-agent-task-board.md` | task queue + parked build tasks |
| `logs/code-worker/2026-03-14-23.md` through `2026-03-15-00c.md` | code-worker research cycle records |

---

## first implementation slice

### what: `memory-ledger`

### scope
- Supabase/Postgres schema implementing note 13's 7 object families
- SQL migration(s) producing: `owners`, `purrs`, `episodes`, `session_windows`, `message_events`, `memory_items`, `memory_events`, `memory_evidence_refs`, `pack_artifacts`
- `pack_candidate_view` as a SQL view
- RLS policies enforcing owner-scoped reads
- Partial unique indexes for active-truth uniqueness
- Foreign keys and index set from note 13 section 6
- Minimal typed API (write-side: open/close windows, append messages, create/confirm/challenge/supersede/reject memory, store packs; read-side: get active window, get pack candidates, get latest pack, get evidence)
- Local test fixtures: at least one owner, one purr, one episode, one window, sample memory items across all 8 v1 kinds, sample evidence refs, sample pack artifact
- README with setup instructions (Supabase project, local dev, migration commands)

### not in this slice
- vector search / pgvector
- catnet tables
- multimodal evidence
- user-facing UI
- LLM-based extraction logic
- actual pack generation logic

### inputs to consume
- `ily/13` (primary schema spec)
- `ily/14` (runtime write-path rules, idempotency)
- `ily/12` (claim shapes, selection model)
- `ily/11` (session/episode scope)
- `ily/08` (lifecycle states, contradiction handling)

### acceptance criteria (from note 13 section 10)
- every `memory_item` carries `owner_id` + `purr_id` with valid scope fields
- candidate cannot be created without at least one evidence ref
- explicit correction supersedes old preference without leaving both active in the same exclusive dedupe scope
- contradiction challenges active truth and suppresses it from pack candidates in one transaction
- `pack_candidate_view` hides challenged/superseded/rejected rows from hard-truth lanes
- all 4 pack types can be stored immutably and queried by boundary
- warm re-entry can open a child `session_window` without mutating old window history
- exact evidence lookup returns the original message/span even if later summaries exist
- `memory_event` trail explains every current state transition
- no cross-owner read possible
- vector search is not required

---

## next 3 concrete manual tasks

### task 1 — close research-first phase on the task board
update `notes/boards/weekly-missions.md` to explicitly mark research-first phase as closed.
update `notes/boards/coding-agent-task-board.md` to move `memory-ledger` from `parked` to `queued` with pick order 19.
this is a gooner decision — code-worker should not self-promote tasks.

### task 2 — set up Supabase project and document connection
create Supabase project (or document how to use local dev with `supabase init` + `supabase start`).
add connection pattern to the repo so code-worker can run migrations.
this blocks every build task.

### task 3 — code-worker builds memory-ledger
once tasks 1 and 2 are done, code-worker picks `memory-ledger`, consumes notes 08/11/12/13/14, and ships:
- SQL migration(s)
- typed API
- test fixtures
- README
in `tools/memory-ledger/`.

---

## what must stay parked

| item | reason |
|------|--------|
| catnet posting / markets | private memory works first (note 10, alignment brief) |
| social memory graph | after single-purr memory (task board) |
| multimodal memory ingest | text loop first (task board) |
| purr world sim | city after memory spine (task board) |
| vector search | not in v1 ledger (note 13, explicit) |
| user-facing memory UI | chat-first, no dashboard (alignment brief) |
| moltbook / poly archived work | dead lane, do not resurrect (AGENTS.md) |

---

## direct answers

### are code-worker and gooner actually in sync?
**yes.** no meaningful drift detected. code-worker independently verified Hermes findings and reached the same architecture conclusions. gooner extended depth with notes 12-20. the contracts are consistent. both agents agree on first build slice, identity model, lifecycle states, pack discipline, and product voice.

### is research-first phase actually ready to close?
**yes, with one caveat.** all 18 research tasks are done. all 4 weekly mission success criteria are checked. the ily/ notes cover every contract surface needed for the first 3 build slices. the caveat is that Supabase project setup (gap 6) must happen before code-worker can actually build. but that is an operational prerequisite, not a research gap.

### is memory-ledger still the first build slice?
**yes.** every note that discusses build order converges here. the reasoning is unchanged: extractor needs somewhere to write, packer needs something to read, feedback loop needs state to transition, salvage needs a target store. the ledger is the truth backbone. note 13 provides enough schema detail that a builder can start without guessing.

### what is the single critical thing missing before build starts?
**Supabase project setup + connection documentation.** the repo assumes Supabase everywhere but has no project URL, no local dev setup, no migration runner. code-worker cannot ship a SQL migration if there is nowhere to run it. this is the one blocker.

---

## short verdict
research-first phase produced a serious body of work across 16 architecture notes, 4 code-worker research cycles, and 5 board files. no drift between agents. no fake progress. the contracts are specific enough to build from.

the repo is ready to close research and open the first build slice. the only operational blocker is Supabase setup.
